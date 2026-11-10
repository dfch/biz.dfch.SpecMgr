workspace "Parcel Tracker" "Tracks parcels from dispatch to delivery." {
    model {
        customer = person "Customer" "Looks up the status of their parcels."
        tracker = softwareSystem "Parcel Tracker" "Tracks parcels from dispatch to delivery." {
            portal = container "Web Portal" "Lets customers look up shipments; embeds the shared pricing rules library." "Python/FastAPI"
            dispatch = container "Dispatch Service" "Assigns parcels to couriers; embeds the shared pricing rules library." "Java"
            db = container "Shipments Database" "Stores shipments and dispatch records." "PostgreSQL"
        }
        emailProvider = softwareSystem "Email Delivery Service" "Delivers notification emails on behalf of the platform." "External"
        customer -> portal "tracks parcels through" "HTTPS/JSON"
        portal -> dispatch "requests dispatch status from" "gRPC"
        portal -> db "reads shipment records from" "JDBC"
        dispatch -> db "writes dispatch records to" "JDBC"
        dispatch -> emailProvider "sends notification emails to" "REST/JSON"
    }
    views {
        systemContext tracker "TrackerContext" {
            include *
            autoLayout
        }
    }
}
