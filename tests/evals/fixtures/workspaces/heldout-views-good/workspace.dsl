workspace "Claims Center" "Insurance claims for policyholders." {
    model {
        policyholder = person "Policyholder" "Reports claims and tracks their progress."
        claims = softwareSystem "Claims Center" "The insurer's claims platform." {
            web = container "Web Portal" "Where policyholders report claims and track their progress." "Python/FastAPI" "Web"
            mobile = container "Mobile App Backend" "Serves the insurer's mobile app." "Go" "Web"
            intake = container "Claims Intake Service" "Registers new claims." "Java/Spring"
            triage = container "Triage Service" "Classifies and prioritizes claims." "Java/Spring"
            assessment = container "Assessment Service" "Calculates settlement amounts." "Kotlin"
            payout = container "Payout Service" "Executes claim settlements." "Java/Spring"
            fraudScreening = container "Fraud Screening Service" "Flags suspicious claims." "Python"
            docService = container "Document Service" "Accepts claim photos and reports." "Node.js"
            notifications = container "Notification Service" "Emails and messages policyholders." "Node.js"
            assignment = container "Assignment Service" "Routes claims to adjusters." "Java/Spring"
            workbench = container "Adjuster Workbench" "Where staff process their assigned claims." "Vue" "Web"
            policyVerification = container "Policy Verification Service" "Checks that a claim is covered by the policy." "Java/Spring"
            reinsurance = container "Reinsurance Allocation Service" "Apportions large losses across reinsurance partners." "Java/Spring"
            batch = container "Batch Scheduler" "Runs the nightly reserves calculation." "Java"
            queue = container "Event Queue" "Carries claim events between the application parts." "RabbitMQ" "Queue"
            claimsDb = container "Claims Database" "Stores claim records." "PostgreSQL" "Database"
            policyDb = container "Policy Database" "Stores policy and cover records." "PostgreSQL" "Database"
            auditDb = container "Audit Database" "Stores the compliance audit trail." "PostgreSQL" "Database"
            docStore = container "Document Store" "Holds claim photos, reports, and correspondence." "S3"
        }
        dataBureau = softwareSystem "National Claims Data Bureau" "Holds historical claims records." "External"
        clearingHouse = softwareSystem "Clearing House" "Executes settlement transfers between institutions." "External"

        policyholder -> web "Reports claims through" "HTTPS/JSON"
        policyholder -> mobile "Reports claims through" "HTTPS/JSON"
        web -> intake "Submits new claims to" "gRPC"
        web -> assessment "Requests settlement quotes from" "gRPC"
        web -> payout "Requests settlements from" "gRPC"
        web -> docService "Uploads claim documents to" "gRPC"
        web -> notifications "Subscribes to status updates from" "gRPC"
        mobile -> intake "Submits new claims to" "gRPC"
        mobile -> assessment "Requests settlement quotes from" "gRPC"
        mobile -> payout "Requests settlements from" "gRPC"
        intake -> triage "Hands accepted claims to" "gRPC"
        intake -> fraudScreening "Screens each incoming claim with" "gRPC"
        intake -> policyVerification "Checks the cover with" "gRPC"
        intake -> queue "Publishes claim events to" "AMQP"
        triage -> assessment "Routes claims to" "gRPC"
        triage -> assignment "Routes the claim to" "gRPC"
        assessment -> payout "Requests settlements from" "gRPC"
        assessment -> reinsurance "Apportions large losses to" "gRPC"
        assignment -> workbench "Allocates claims to" "gRPC"
        workbench -> claimsDb "Reads and writes claim records in" "SQL"
        workbench -> auditDb "Writes audit entries to" "SQL"
        fraudScreening -> dataBureau "Consults historical claims at" "HTTPS/JSON"
        payout -> clearingHouse "Executes settlements through" "ISO 20022"
        docService -> docStore "Stores photos and reports in" "HTTPS/JSON"
        notifications -> queue "Consumes claim events from" "AMQP"
        notifications -> claimsDb "Reports claim status changes from" "SQL"
        batch -> claimsDb "Recalculates reserves in" "SQL"
        batch -> policyDb "Reconciles cover in" "SQL"
    }
    views {
        systemContext claims "PolicyholderContext" {
            include *
            autoLayout
        }
        container claims "ClaimIntake" {
            include policyholder
            include web
            include mobile
            include intake
            include triage
            include fraudScreening
            include policyVerification
            include queue
            autoLayout
        }
        container claims "ClaimProcessing" {
            include assignment
            include workbench
            include assessment
            include reinsurance
            include payout
            include queue
            autoLayout
        }
        container claims "ClaimSupport" {
            include docService
            include docStore
            include notifications
            include batch
            include claimsDb
            include policyDb
            include auditDb
            autoLayout
        }
    }
}
