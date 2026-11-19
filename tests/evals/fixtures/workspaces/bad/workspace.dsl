workspace "Broken" "A workspace with a syntax error (missing closing brace)." {
    model {
        customer = person "Customer" "Buys books online."
        bookshop = softwareSystem "Bookshop" "Sells books." {
            web = container "Web Store" "The web shop." "Python"
        customer -> web "Uses" "HTTPS"
    }
