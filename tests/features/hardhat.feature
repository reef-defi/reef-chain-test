Feature: hardhat

  Scenario: Deploy flipper contract and flip it
    Given I deploy a flipper contract using hardhat
    When I call the flip method on the contract
    Then I receive the opposite result

  Scenario: Deploy all integration contracts and verify them
    Given I deploy a colletion of contracts using hardhat
    Then I expect the script to output given results