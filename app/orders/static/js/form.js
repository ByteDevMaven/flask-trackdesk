document.addEventListener("DOMContentLoaded", () => {
    const itemsContainer = document.getElementById("items-container")
    const addItemBtn = document.getElementById("add-item-btn")
    const modal = document.getElementById("product-picker-modal")
    const closeModalBtn = document.getElementById("close-modal")
    const productSearch = document.getElementById("product-search")
    const productsList = document.getElementById("products-list")
    const noResults = document.getElementById("no-results")

    let itemIndex = itemsContainer.children.length
    let currentRow = null
    const currency = document.getElementById("currencySymbol").value

    addItemBtn.addEventListener("click", () => {
        const container = document.getElementById("items-container")
        const newRow = createItemRow(itemIndex)
        container.appendChild(newRow)
        itemIndex++
        updateOrderTotal()
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

    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.classList.add("hidden")
            currentRow = null
        }
    })

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
            const productCode = card.dataset.code ?? ""
            const productPrice = card.dataset.price

            currentRow.querySelector(".item-id-input").value = productId

            currentRow.querySelector(".product-name").textContent = productName
            currentRow.querySelector(".product-name").classList.remove("text-fg-muted")

            currentRow.querySelector(".code-input").value = productCode

            currentRow.querySelector(".item-price").value = Number.parseFloat(productPrice).toFixed(2)

            updateRowTotal(currentRow)
            updateOrderTotal()

            modal.classList.add("hidden")
            currentRow = null
        }
    })

    itemsContainer.addEventListener("click", (e) => {
        if (e.target.closest(".remove-item")) {
            const row = e.target.closest(".item-row")
            if (itemsContainer.children.length > 1) {
                row.remove()
                updateOrderTotal()
            } else {
                alert("At least one item is required")
            }
        }
    })

    itemsContainer.addEventListener("input", (e) => {
        if (e.target.matches(".item-quantity, .item-price")) {
            updateRowTotal(e.target.closest(".item-row"))
            updateOrderTotal()
        }
    })

    function createItemRow(index) {
        const div = document.createElement('tbody')
        div.innerHTML = `
      <tr class="item-row hover:bg-primary-50" data-item-id="">
        <td class="px-4 py-3">
          <input type="hidden" name="items[${index}][inventory_item_id]" value="" class="item-id-input">
          <button type="button" class="select-product-btn w-full px-3 py-2 text-left text-sm border border-primary-300 rounded-lg hover:bg-primary-50 focus:ring-accent-500 focus:border-accent-500 bg-bg-base text-fg-base flex items-center justify-between">
            <span class="product-name text-fg-muted">Select a product</span>
            <i class="fas fa-search text-fg-muted text-xs"></i>
          </button>
        </td>
        <td class="px-4 py-3">
          <input type="text" name="items[${index}][code]" 
            class="code-input w-full px-2 py-1 text-sm border border-primary-300 rounded focus:ring-accent-500 focus:border-accent-500 bg-bg-base text-fg-base">
        </td>
        <td class="px-4 py-3">
          <input type="number" name="items[${index}][quantity]" value="1" min="1"
            class="w-full px-2 py-1 text-sm border border-primary-300 rounded focus:ring-accent-500 focus:border-accent-500 item-quantity bg-bg-base text-fg-base">
        </td>
        <td class="px-4 py-3">
          <input type="number" name="items[${index}][price]" value="0.00" min="0" step="0.01"
            class="w-full px-2 py-1 text-sm border border-primary-300 rounded focus:ring-accent-500 focus:border-accent-500 item-price bg-bg-base text-fg-base">
        </td>
        <td class="px-4 py-3">
          <div class="item-total font-medium text-fg-base text-sm">${currency}0.00</div>
        </td>
        <td class="px-4 py-3 text-center">
          <button type="button" class="text-btn-danger-bg hover:text-btn-danger-hover remove-item p-1 rounded">
            <i class="fas fa-trash text-sm"></i>
          </button>
        </td>
      </tr>
    `
        return div.querySelector('tr')
    }

    function updateRowTotal(row) {
        const quantity = parseFloat(row.querySelector(".item-quantity")?.value) || 0
        const price = parseFloat(row.querySelector(".item-price")?.value) || 0
        const total = quantity * price
        row.querySelector(".item-total").textContent = currency + total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }

    function updateOrderTotal() {
        let total = 0
        document.querySelectorAll(".item-row").forEach(row => {
            const quantity = parseFloat(row.querySelector(".item-quantity")?.value) || 0
            const price = parseFloat(row.querySelector(".item-price")?.value) || 0
            total += quantity * price
        })
        document.getElementById("order-total").textContent = currency + total.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }

    // Initial calculation
    document.querySelectorAll(".item-row").forEach(updateRowTotal)
    updateOrderTotal()
})
