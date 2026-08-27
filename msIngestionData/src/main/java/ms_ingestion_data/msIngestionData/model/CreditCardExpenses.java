import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class CreditCardExpenses {
    
    public String cardFinalNumber;
    public String cardOwner;
    public String cardBank;
    public String cardName;
    public BigDecimal cardAmount;
    public LocalDate cardExpensesDate;

    public CreditCardExpenses(String cardFinalNumber, String cardOwner, String cardBank, String cardName, BigDecimal cardAmount, LocalDate cardExpensesDate) {
        this.cardFinalNumber = cardFinalNumber;
        this.cardOwner = cardOwner;
        this.cardBank = cardBank;
        this.cardName = cardName;
        this.cardAmount = cardAmount;
        this.cardExpensesDate = cardExpensesDate;
    }

    public CreditCardExpenses() {}

    public String getCardFinalNumber() {
        return cardFinalNumber;
    }

    public void setCardFinalNumber(String cardFinalNumber) {
        this.cardFinalNumber = cardFinalNumber;
    }

    public String getCardOwner() {
        return cardOwner;
    }

    public void setCardOwner(String cardOwner) {
        this.cardOwner = cardOwner;
    }

    public String getCardBank() {
        return cardBank;
    }

    public void setCardBank(String cardBank) {
        this.cardBank = cardBank;
    }

    public String getCardName() {
        return cardName;
    }

    public void setCardName(String cardName) {
        this.cardName = cardName;
    }

    public BigDecimal getCardAmount() {
        return cardAmount;
    }

    public void setCardAmount(BigDecimal cardAmount) {
        this.cardAmount = cardAmount;
    }

    public LocalDate getCardExpensesDate() {
        return cardExpensesDate;
    }

    public void setCardExpensesDate(LocalDate cardExpensesDate) {
        this.cardExpensesDate = cardExpensesDate;
    }


    public Map<String, BigDecimal> totalAmountByCard(List<CardExpense> expenses) {

        return expenses.stream()
                .collect(Collectors.groupingBy(
                        expense -> expense.cardFinalNumber,
                        Collectors.reducing(
                                BigDecimal.ZERO,
                                expense -> expense.cardAmount,
                                BigDecimal::add
                        )
                ));
    }


}
