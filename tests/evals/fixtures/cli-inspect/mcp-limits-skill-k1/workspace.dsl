workspace "Bookshop" "A simple online bookshop" {
    model {
        customer = person "Customer" "A customer who browses and buys books"
        bookshop = softwareSystem "Bookshop" "An online bookshop that sells books to customers" {
            catalogue = container "Catalogue" "Lets customers browse and search the book catalogue" "Java, Spring Boot"
            basket = container "Basket" "Holds the books a customer has selected for purchase" "Java, Spring Boot"
            orders = container "Orders" "Records and processes customer orders" "Java, Spring Boot"
            database = container "Database" "Stores books, baskets and orders" "PostgreSQL 16"
        }
        payments = softwareSystem "Payment Gateway" "A third-party service that charges customer cards"

        customer -> bookshop "Browses books and places orders" "HTTPS"
        bookshop -> payments "Charges the customer's card" "HTTPS/REST"
        basket -> catalogue "Looks up book details" "In-process call"
        basket -> orders "Submits the basket as an order" "In-process call"
        catalogue -> database "Reads book records" "JDBC"
        orders -> database "Persists order records" "JDBC"
    }
    configuration {
        scope softwaresystem
    }
    views {
        systemContext bookshop "SystemContext" "Shows the Bookshop and the people and systems that interact with it" {
            include *
            autoLayout
        }
        container bookshop "Containers" "Shows the containers that make up the Bookshop" {
            include *
            autoLayout
        }
    }
}
