Feature: hardhat

    Scenario: Deploy flipper contract and flip it
        Given I deploy a flipper contract using hardhat
        When I call the flip method on the contract
        Then I receive the opposite result