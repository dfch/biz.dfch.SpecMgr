workspace "bad-duplicate-perspective" {
    model {
        s = softwareSystem "S" {
            perspectives {
                "Reliability" "first" "Satisfactory"
                "Reliability" "second" "Unsatisfactory"
            }
        }
    }
}
