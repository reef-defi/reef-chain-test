Feature: transfer

  Scenario: Alice sends funds to Bob
    Given We have balances for Alice and Bob
    When Alice sends 100000 REEF to Bob
    Then Alices balance decreases by 100000 REEF + fees and Bobs balance increases by 100000 REEF
