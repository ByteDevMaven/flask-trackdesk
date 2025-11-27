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

  addItemBtn.addEventListener("click", async () => {
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
      // Replace select with button
      const selectTd = row.querySelector("td:first-child")
      const selectElement = selectTd.querySelector("select")
      const itemId = selectElement ? selectElement.value : ""

      selectTd.innerHTML = `
                <input type="hidden" name="items[${itemIndex}][inventory_item_id]" value="${itemId}" class="item-id-input">
                <button type="button" class="select-product-btn w-full px-3 py-2 text-left text-sm border border-secondary-200 rounded-lg hover:bg-secondary-50 focus:ring-accent-500 focus:border-accent-500 bg-bg-base text-fg-base flex items-center justify-between">
                    <span class="product-name text-fg-muted">${selectElement && selectElement.selectedOptions[0] ? selectElement.selectedOptions[0].text : "Select a product"}</span>
                    <i class="fas fa-search text-fg-muted text-xs"></i>
                </button>
            `

      itemsContainer.appendChild(row)
      itemIndex++
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
      const productId = card.dataset.id
      const productName = card.dataset.name
      const productDescription = card.dataset.description
      const productPrice = card.dataset.price
      const productStock = card.dataset.stock

      // Update hidden input
      currentRow.querySelector(".item-id-input").value = productId

      // Update button text
      currentRow.querySelector(".product-name").textContent = productName
      currentRow.querySelector(".product-name").classList.remove("text-fg-muted")

      // Update description
      currentRow.querySelector(".item-description").value = productDescription

      // Update price
      currentRow.querySelector(".item-price").value = Number.parseFloat(productPrice).toFixed(2)

      const qtyInput = currentRow.querySelector(".item-quantity")
      if (!qtyInput.value || Number(qtyInput.value) <= 0) {
        qtyInput.value = 1
      }

      // Update quantity max
      currentRow.querySelector(".item-quantity").setAttribute("max", productStock)

      updateRowTotal(currentRow)
      updateTotals()

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
    const tax18 = subtotal * 0
    const total = subtotal + tax15 + tax18

    document.getElementById("subtotal").textContent = currency + subtotal.toFixed(2)
    document.getElementById("tax-15").textContent = currency + tax15.toFixed(2)
    document.getElementById("tax-18").textContent = currency + tax18.toFixed(2)
    document.getElementById("total").textContent = currency + total.toFixed(2)
  }

  // Initialize
  document.querySelectorAll(".item-row").forEach(updateRowTotal)
  updateTotals()
})