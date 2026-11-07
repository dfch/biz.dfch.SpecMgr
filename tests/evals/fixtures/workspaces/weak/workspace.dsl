workspace "Weak" "A valid but thin workspace: one container, no views, one relationship without a technology." {
    model {
        customer = person "Customer" "Buys books online."
        bookshop = softwareSystem "Bookshop" "Sells books to customers." {
            web = container "Web Store" "The customer-facing web shop." "Python"
        }
        customer -> web "Orders books through"
        web -> web "Self" "HTTPS"
    }
}
