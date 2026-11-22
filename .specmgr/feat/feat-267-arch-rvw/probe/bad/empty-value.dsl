workspace "bad-empty-value" {
    model {
        s = softwareSystem "S" {
            properties {
                "trust.boundary" ""
            }
        }
    }
}
