workspace "Museum Ticketing" "Sells and validates museum entry." {
    model {
        visitor = person "Museum Visitor" "Buys tickets and plans visits."
        payment = element "Payment Provider" "Processes card payments."
        ticketing = softwareSystem "Museum Ticketing" "Sells tickets and manages entry." {
            shop = container "Ticket Shop" "Online ticket sales." "Python"
            kiosk = container "Ticket Kiosk" "On-site self-service ticket sales." "Java"
            scanner = container "Entry Scanner" "Validates tickets at the door." "C/C++"
        }
        scanner -> shop "Validates tickets in" "gRPC"
        shop -> payment "Authorises charges to" "REST/JSON"
        visitor -> shop "Buys tickets through" "HTTPS"
    }
    views {
        systemContext ticketing "TicketingContext" {
            include *
            autoLayout
        }
    }
}
