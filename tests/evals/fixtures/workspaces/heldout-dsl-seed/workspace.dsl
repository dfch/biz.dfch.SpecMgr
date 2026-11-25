workspace "Museum Ticketing" "Sells and validates museum entry." {
    model {
        visitor = person "Museum Visitor" Buys tickets and plans visits
        ticketing = softwareSystem "Museum Ticketing" "Sells tickets and manages entry." {
            shop = container "Ticket Shop" "Online ticket sales." "Python"
            shop = container "Ticket Kiosk"
            scanner = container "Entry Scanner" "Validates tickets at the door." "C/C++"
        }
        scanner -> shop "Validates tickets in" "gRPC"
        shop -> payment "Authorises charges to" "REST/JSON"
        payment = element "Payment Provider" "Processes card payments."
        visitor -> shop "Buys tickets through"
    }
    views {
        systemContext ticketing "TicketingContext" {
            include *
            autoLayout
        }
    }
}
