workspace "duplicate-property-parses" {
    model {
        s = softwareSystem "S" {
            properties {
                "review.criterion" "VP06-RE-100"
                "review.criterion" "VP06-RE-110"
            }
        }
    }
}
