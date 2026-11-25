workspace "Bank Portal" "Online banking for customers." {
    model {
        customer = person "Bank Customer" "Manages accounts, moves money, and tracks activity."
        bank = softwareSystem "Bank Portal" "The company's online banking platform." {
            web = container "Web Portal" "Where customers log in and manage their accounts." "Python/FastAPI" "Web"
            mobile = container "Mobile App Backend" "Serves the bank's mobile app." "Go" "Web"
            accounts = container "Account Service" "Holds the customer account records." "Java/Spring"
            transactions = container "Transaction Service" "Processes deposits, withdrawals, and transfers." "Java/Spring"
            payments = container "Payment Service" "Executes card payments and bank transfers." "Java/Spring"
            cards = container "Card Service" "Manages debit and credit cards." "Kotlin"
            fraud = container "Fraud Detection Service" "Scores transactions for fraud." "Python"
            notifications = container "Notification Service" "Sends email and SMS alerts." "Node.js"
            onboarding = container "Onboarding Service" "Verifies new customers." "Python"
            statements = container "Statements Service" "Generates monthly statements." "Java/Spring"
            directDebit = container "Direct Debit Service" "Processes standing orders and direct debits." "Java/Spring"
            exchangeRates = container "Exchange Rates Service" "Provides currency conversion rates." "Go"
            batch = container "Batch Scheduler" "Runs the nightly interest calculation and reconciliation." "Java"
            queue = container "Event Queue" "Carries internal events between the application parts." "RabbitMQ" "Queue"
            ledger = container "Ledger Database" "Stores every account movement." "PostgreSQL" "Database"
            customersDb = container "Customer Database" "Stores account and profile records." "PostgreSQL" "Database"
            auditDb = container "Audit Database" "Stores the compliance audit trail." "PostgreSQL" "Database"
            cache = container "Cache" "Stores sessions and frequently read account data." "Redis"
            documents = container "Document Store" "Holds the generated statement PDFs." "S3"
        }
        cardNetwork = softwareSystem "Card Payment Network" "Authorises card payments." "External"
        creditAgency = softwareSystem "Credit Reference Agency" "Provides credit checks for onboarding." "External"

        customer -> web "Manages accounts through" "HTTPS/JSON"
        customer -> mobile "Manages accounts through" "HTTPS/JSON"
        web -> accounts "Queries and updates accounts in" "gRPC"
        web -> transactions "Initiates deposits and transfers in" "gRPC"
        web -> payments "Initiates card and bank transfers in" "gRPC"
        web -> statements "Requests statements from" "gRPC"
        web -> directDebit "Manages standing orders in" "gRPC"
        web -> cache "Reads and writes sessions in" "RESP"
        mobile -> accounts "Queries and updates accounts in" "gRPC"
        mobile -> transactions "Initiates deposits and transfers in" "gRPC"
        mobile -> payments "Initiates card and bank transfers in" "gRPC"
        transactions -> ledger "Records every movement in" "SQL"
        transactions -> fraud "Scores each transaction with" "gRPC"
        transactions -> queue "Publishes transaction events to" "AMQP"
        transactions -> auditDb "Writes audit entries to" "SQL"
        payments -> cardNetwork "Routes card authorisations through" "ISO 8583"
        payments -> exchangeRates "Fetches conversion rates from" "gRPC"
        payments -> cards "Checks card status in" "gRPC"
        onboarding -> creditAgency "Requests credit checks from" "HTTPS/JSON"
        onboarding -> customersDb "Stores verified profiles in" "SQL"
        fraud -> queue "Publishes fraud alerts to" "AMQP"
        notifications -> queue "Consumes events from" "AMQP"
        statements -> ledger "Reads account movements from" "SQL"
        statements -> documents "Writes statement PDFs to" "HTTPS/JSON"
        batch -> ledger "Recalculates interest in" "SQL"
        batch -> customersDb "Reconciles profiles in" "SQL"
        directDebit -> transactions "Creates standing-order transfers in" "gRPC"
        accounts -> customersDb "Reads and writes account records in" "SQL"
    }
    views {
        systemContext bank "CustomerContext" {
            include *
            autoLayout
        }
        container bank "FrontOffice" {
            include customer
            include web
            include mobile
            include accounts
            include transactions
            include payments
            include notifications
            include cache
            autoLayout
        }
        container bank "RiskCompliance" {
            include fraud
            include onboarding
            include creditAgency
            include cards
            include auditDb
            autoLayout
        }
        container bank "BackOffice" {
            include statements
            include directDebit
            include exchangeRates
            include batch
            include queue
            include ledger
            include customersDb
            include documents
            autoLayout
        }
    }
}
