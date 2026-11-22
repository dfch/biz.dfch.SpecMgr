workspace extends ../workspace.dsl {
    name "c4-probe review overlay"

    model {
        !element shop.db {
            perspectives {
                "VP03-SE-090" "Documented. One schema for all tenants. Overlay test." "Partially"
            }
            properties {
                "review.overlay" "yes"
            }
        }
    }
}
