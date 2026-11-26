workspace "Bookshop" "A small online bookshop." {
    model {
        customer = person "Customer" "Buys books online."
        bookshop = softwareSystem "Bookshop" "Sells books to customers." {
            web = container "Web Store" "The customer-facing web shop." "Python"
            orders = container "Order Processor" "Takes and processes orders." "Java"
        }
        customer -> web "Orders books through" "HTTPS"
        web -> orders "Submits orders to" "gRPC"
    }
    views {
        systemContext bookshop "SystemContext" {
            include *
            autoLayout
        }
    }
}
