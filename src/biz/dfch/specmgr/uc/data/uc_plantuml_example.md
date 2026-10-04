' The complete, fully attributed sequence diagram for the packaged "Buy Goods" example UC
' (uc/data/uc_example.md) — the model for the generate_uc_sequence_diagram prompt flow
' (Phase 120). This file IS render_uc_sequence_skeleton(example UC) with each UNATTRIBUTED
' marker line replaced by a reasoned attribution (rulebook §2.9.3, applied by understanding the
' free text); the pinning test in tests/uc/models/v2/test_renderer.py asserts that. Every
' attribution comment below explains the reasoning where the text alone does not carry it.
@startuml Buy Goods

actor Buyer
actor "Credit card company" as p2
actor Bank
actor "Shipping service" as p4
participant Company

note
  We know Buyer (customer record exists in system)
  We know Buyer's address
  Buyer has valid contact information on file
end note

' Attribution (was UNATTRIBUTED trigger): the Goal in Context names the Buyer as the one who
' issues the request, so the trigger is the Buyer's action into the system (receiver fixed to the
' system per §2.9.5).
Buyer -> Company: Purchase request comes in (via phone, fax, web form, or electronic interchange)
Buyer -> Company: Buyer calls in with a purchase request.
note right
  Step 1: Buyer may use
  Phone call
  Fax
  Web order form
  Electronic data interchange (EDI)
end note
Company -> Buyer: Company captures buyer's name, address, requested goods, quantity, and delivery date preference.
note right
  Step 2: Company may capture information via
  Manual entry by customer service representative
  Automated web form
  EDI system
end note
Company -> Company: Company checks inventory for requested goods.
note right
  This will use our trusty IBM OS/390 green screen application. Very fast!:

  - Item 1
  - Item 2
  - Item 3
end note
alt Company is out of one of the ordered items
Company -> Buyer: Company informs buyer of out-of-stock items.\nThis should rarely happen. Still we have to address this.
Buyer -> Company: Buyer chooses to: (a) wait for restock, (b) substitute with similar item, or (c) remove item from order.
note right
  Return to step 4.
end note
end
Company -> Buyer: Company gives buyer information on goods, prices, delivery dates, and availability.
alt Buyer requests expedited shipping
Company -> Company: Company calculates expedited shipping cost.
Company -> Buyer: Company provides expedited shipping quote to buyer.
Buyer -> Company: Buyer accepts or declines expedited shipping.
note right
  Return to step 5.
end note
end
Buyer -> Company: Buyer confirms order details and signs for order.
alt Buyer pays directly with credit card
Buyer -> Company: Buyer provides credit card information.
Company -> Company: Company takes payment by credit card (UC-044).
note right
  Continue to step 6.
end note
end
Company -> Company: Company creates order in system.
Company -> Buyer: Company ships order to buyer.
note right
  Step 7: Company may ship via
  Standard ground shipping
  Expedited shipping
  Overnight shipping
  Local pickup
end note
alt Shipping service is unavailable
Company -> p4: Company attempts to use backup shipping service.
' Attribution (was UNATTRIBUTED ext 7a step 2): the sentence itself names the actors — company
' informs buyer.
Company -> Buyer: If backup service also unavailable, company informs buyer of delay.
Company -> Company: Company retries shipping when service becomes available.
end
Company -> Buyer: Company ships invoice to buyer.
alt Invoice delivery fails
Company -> Company: Company retries invoice delivery via alternate channel (email, fax, mail).
' Attribution (was UNATTRIBUTED ext 8a step 2): internal Company logging (no other actor is
' involved) — a self-message.
Company -> Company: If all channels fail, company logs issue for manual follow-up.
end
Buyer -> Company: Buyer receives goods and verifies order.
Buyer -> Company: Buyer pays invoice.
note right
  Step 10: Buyer may pay via
  Cash or money order
  Check
  Credit card
  Debit card
  Bank transfer
  Digital wallet
end note
alt Buyer returns goods
Buyer -> Company: Buyer initiates return request.
Company -> Company: Company handles returned goods (UC-105).
Company -> Company: Company processes refund or credit.
end
alt Buyer disputes charge
Company -> Company: Company initiates dispute resolution process.
Company -> Buyer: Company provides documentation to buyer.
' Attribution (was UNATTRIBUTED ext 10b step 3): genuinely ambiguous — the resolution of a
' charge dispute is driven by the payment processor, not by the Company or the Buyer; the
' secondary-actor list names the credit card company "for payment processing", so p2 (Credit
' card company) is the most defensible sender.
p2 -> Company: Dispute is resolved (refund, credit, or confirmation of charge).
end
alt Payment fails
Company -> Company: Company retries payment collection.
' Attribution (was UNATTRIBUTED ext 10c step 2): the sentence itself names the actors — company
' contacts buyer.
Company -> Buyer: If retry fails, company contacts buyer to resolve payment issue.
note right
  Once payment is received, continue to step 11.
end note
end
Company -> Company: Company receives payment and records it.

note
  Buyer has goods
  We have money for the goods
  Order is recorded in system
  Invoice is sent to Buyer
end note
note
  We have not sent the goods
  Buyer has not spent the money
  Order is not recorded
end note
@enduml
