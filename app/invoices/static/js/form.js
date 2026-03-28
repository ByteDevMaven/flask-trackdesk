document.addEventListener("DOMContentLoaded", () => {
  const itemsContainer = document.getElementById("items-container")
  const addItemBtn = document.getElementById("add-item")
  const modal = document.getElementById("product-picker-modal")
  const closeModalBtn = document.getElementById("close-modal")
  const productSearch = document.getElementById("product-search")
  const productsList = document.getElementById("products-list")
  const noResults = document.getElementById("no-results")

  let itemIndex = itemsContainer.children.length
  let currentRow = null
  const currency = document.getElementById("currencySymbol").value
  const csrftoken = document.querySelector('input[name="csrf_token"]').value

  function reindexItems() {
    document.querySelectorAll(".item-row").forEach((row, i) => {
      row.querySelector(".item-id-input")?.setAttribute("name", `items[${i}][inventory_item_id]`)
      row.querySelector(".item-description")?.setAttribute("name", `items[${i}][description]`)
      row.querySelector(".item-quantity")?.setAttribute("name", `items[${i}][quantity]`)
      row.querySelector(".item-price")?.setAttribute("name", `items[${i}][unit_price]`)
      row.querySelector(".item-discount")?.setAttribute("name", `items[${i}][discount]`)
    })

    itemIndex = document.querySelectorAll(".item-row").length
  }

  async function addNewRow() {
    const formData = new FormData()
    formData.append("index", itemIndex)
    formData.append("csrf_token", csrftoken)

    const res = await fetch("/invoices/item-row", {
      method: "POST",
      body: formData,
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })

    const html = await res.text()
    const temp = document.createElement("tbody")
    temp.innerHTML = html
    const row = temp.querySelector("tr")

    if (row) {
      itemsContainer.appendChild(row)
      itemIndex++
      return row
    }
    return null
  }

  function populateRow(row, productData) {
    if (!row) return

    // Update hidden input
    row.querySelector(".item-id-input").value = productData.id

    // Update button text
    const nameEl = row.querySelector(".product-name")
    nameEl.textContent = productData.name
    nameEl.classList.remove("text-slate-400", "italic")

    // Update description
    row.querySelector(".item-description").value = productData.description

    // Update price
    row.querySelector(".item-price").value = Number.parseFloat(productData.price).toFixed(2)

    const qtyInput = row.querySelector(".item-quantity")
    if (!qtyInput.value || Number(qtyInput.value) <= 0) {
      qtyInput.value = 1
    }

    // Update quantity max
    qtyInput.setAttribute("max", productData.stock)

    updateRowTotal(row)
    updateTotals()
  }

  addItemBtn.addEventListener("click", async () => {
    const row = await addNewRow()
    if (row) {
      updateRowTotal(row)
      updateTotals()
    }
  })

  itemsContainer.addEventListener("click", (e) => {
    const btn = e.target.closest(".select-product-btn")
    if (btn) {
      currentRow = btn.closest(".item-row")
      modal.classList.remove("hidden")
      productSearch.value = ""
      productSearch.focus()
      filterProducts("")
    }
  })

  closeModalBtn.addEventListener("click", () => {
    modal.classList.add("hidden")
    currentRow = null
  })

  // Close modal on outside click
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.classList.add("hidden")
      currentRow = null
    }
  })

  // Close modal on Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !modal.classList.contains("hidden")) {
      modal.classList.add("hidden")
      currentRow = null
    }
  })

  productSearch.addEventListener("input", (e) => {
    filterProducts(e.target.value.toLowerCase())
  })

  function filterProducts(searchTerm) {
    const productCards = productsList.querySelectorAll(".product-card")
    let visibleCount = 0

    productCards.forEach((card) => {
      const searchData = card.dataset.search
      if (searchData.includes(searchTerm)) {
        card.classList.remove("hidden")
        visibleCount++
      } else {
        card.classList.add("hidden")
      }
    })

    if (visibleCount === 0) {
      noResults.classList.remove("hidden")
      productsList.classList.add("hidden")
    } else {
      noResults.classList.add("hidden")
      productsList.classList.remove("hidden")
    }
  }

  productsList.addEventListener("click", (e) => {
    const card = e.target.closest(".product-card")
    if (card && currentRow) {
      populateRow(currentRow, {
        id: card.dataset.id,
        name: card.dataset.name,
        description: card.dataset.description,
        price: card.dataset.price,
        stock: card.dataset.stock
      })

      modal.classList.add("hidden")
      currentRow = null
    }
  })

  // Remove item
  itemsContainer.addEventListener("click", (e) => {
    if (e.target.closest(".remove-item")) {
      const row = e.target.closest(".item-row")
      if (itemsContainer.children.length > 1) {
        row.remove()
        reindexItems()
        updateTotals()
      }
    }
  })

  // Update totals on input
  itemsContainer.addEventListener("input", (e) => {
    if (e.target.matches(".item-quantity, .item-price, .item-discount")) {
      updateRowTotal(e.target.closest(".item-row"))
      updateTotals()
    }
  })

  function updateRowTotal(row) {
    const q = Number.parseFloat(row.querySelector(".item-quantity")?.value || 0)
    const p = Number.parseFloat(row.querySelector(".item-price")?.value || 0)
    const d = Number.parseFloat(row.querySelector(".item-discount")?.value || 0)
    const subtotal = q * p
    const discount = subtotal * (d / 100)
    const total = subtotal - discount
    row.querySelector(".item-total").textContent = currency + total.toFixed(2)
  }

  function updateTotals() {
    let subtotal = 0
    document.querySelectorAll(".item-row").forEach((row) => {
      const q = Number.parseFloat(row.querySelector(".item-quantity")?.value || 0)
      const p = Number.parseFloat(row.querySelector(".item-price")?.value || 0)
      const d = Number.parseFloat(row.querySelector(".item-discount")?.value || 0)
      const itemSubtotal = q * p
      const itemDiscount = itemSubtotal * (d / 100)
      subtotal += itemSubtotal - itemDiscount
    })

    const tax15 = subtotal * 0.15
    const total = subtotal + tax15

    const subtotalEl = document.getElementById("subtotal")
    const tax15El = document.getElementById("tax-15")
    const totalEl = document.getElementById("total")

    if (subtotalEl) subtotalEl.textContent = currency + subtotal.toFixed(2)
    if (tax15El) tax15El.textContent = currency + tax15.toFixed(2)
    if (totalEl) totalEl.textContent = currency + total.toFixed(2)
  }

  // Barcode Scanner Logic
  const barcodeScan = document.getElementById("barcode-scan")

  barcodeScan?.addEventListener("keydown", async (e) => {
    if (e.key === "Enter") {
      e.preventDefault()
      const value = barcodeScan.value.trim()
      if (!value) return

      const productCards = productsList.querySelectorAll(".product-card")
      let foundCard = null

      // Search by barcode first, then by ID
      productCards.forEach(card => {
        if (card.dataset.barcode === value || card.dataset.id === value) {
          foundCard = card
        }
      })

      // If not found, try name match (only if unique)
      if (!foundCard) {
        const matches = []
        productCards.forEach(card => {
          if (card.dataset.name.toLowerCase().includes(value.toLowerCase())) {
            matches.push(card)
          }
        })
        if (matches.length === 1) {
          foundCard = matches[0]
        }
      }

      if (foundCard) {
        // Check if item already exists in the list
        const existingRow = Array.from(document.querySelectorAll(".item-row")).find(row => 
          row.querySelector(".item-id-input").value === foundCard.dataset.id
        )

        if (existingRow) {
          const qtyInput = existingRow.querySelector(".item-quantity")
          qtyInput.value = parseInt(qtyInput.value || 0) + 1
          updateRowTotal(existingRow)
          updateTotals()
          
          // Flash the row to show it was updated
          existingRow.classList.add("bg-indigo-500/10", "transition-all", "duration-300")
          setTimeout(() => existingRow.classList.remove("bg-indigo-500/10"), 1000)
        } else {
          const newRow = await addNewRow()
          if (newRow) {
            populateRow(newRow, {
              id: foundCard.dataset.id,
              name: foundCard.dataset.name,
              description: foundCard.dataset.description,
              price: foundCard.dataset.price,
              stock: foundCard.dataset.stock
            })
            // Flash the new row
            newRow.classList.add("bg-emerald-500/10", "transition-all", "duration-300")
            setTimeout(() => newRow.classList.remove("bg-emerald-500/10"), 1000)
          }
        }
        barcodeScan.value = ""
        barcodeScan.classList.remove("border-rose-500")
      } else {
        // Not found
        barcodeScan.classList.add("border-rose-500")
        setTimeout(() => barcodeScan.classList.remove("border-rose-500"), 2000)
      }
    }
  })

  // Global F2 to focus scan
  document.addEventListener("keydown", (e) => {
    if (e.key === "F2") {
      e.preventDefault()
      barcodeScan?.focus()
    }
  })

  // Initialize
  document.querySelectorAll(".item-row").forEach(updateRowTotal)
  updateTotals()
})