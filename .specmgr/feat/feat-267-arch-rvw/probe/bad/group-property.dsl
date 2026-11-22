workspace "bad-group-property" {
    model {
        s = softwareSystem "S" {
            group "Trust zone" {
                properties {
                    "trust.boundary" "internal"
                }
                c = container "C"
            }
        }
    }
}
