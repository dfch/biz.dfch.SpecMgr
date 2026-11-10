workspace "Energy Manager" "Balances a household's energy use and costs." {
    model {
        homeowner = person "Homeowner" "Manages the household's energy use and costs."
        manager = softwareSystem "Energy Manager" "Balances a household's energy use and costs." {
            dashboard = container "Dashboard Web App" "Shows consumption and costs; embeds the shared rates library." "Python/FastAPI"
            scheduler = container "Scheduling Service" "Plans charging and heating; embeds the shared rates library." "Java"
            readings = container "Readings Database" "Stores meter readings and schedules." "PostgreSQL"
        }
        meterProvider = softwareSystem "Smart Meter Provider" "Publishes live meter readings for the home." "External"
        homeowner -> dashboard "manages household energy through" "HTTPS/JSON"
        dashboard -> readings "reads meter data from" "JDBC"
        scheduler -> readings "writes schedules to" "JDBC"
        scheduler -> meterProvider "fetches live meter readings from" "REST/JSON"
    }
    views {
        systemContext manager "ManagerContext" {
            include *
            autoLayout
        }
    }
}
