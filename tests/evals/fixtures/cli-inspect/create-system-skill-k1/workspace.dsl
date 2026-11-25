workspace "Bookshop" "A simple online bookshop" {
    model {
        customer = person "Customer" "A customer who browses the catalogue and buys books online."
        bookshop = softwareSystem "Bookshop" "An online bookshop where customers can browse, order, and pay for books." {
            webStore = container "Web Store" "The web application customers use to browse the catalogue and place orders." "Java/Spring Boot"
            orderProcessor = container "Order Processor" "Processes and confirms customer orders." "Java/Spring Boot"
        }

        customer -> webStore "Browses the catalogue and places orders through" "HTTPS/HTML"
        webStore -> orderProcessor "Submits new orders to" "HTTP/JSON"
    }

    views {
        systemContext bookshop "SystemContext" "Shows the Bookshop system and its relationship with the Customer." {
            include *
            autoLayout
        }

        container bookshop "Containers" "Shows the containers within the Bookshop system." {
            include *
            autoLayout
        }
    }

    configuration {
        scope softwaresystem
    }
}
