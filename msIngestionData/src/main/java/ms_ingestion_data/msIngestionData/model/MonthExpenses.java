public class MonthExpenses {
    
    private LocalDate expensesDate;
    private String expensesDescription;
    private BigDecimal expensesAmount;
    private String expensesCategory;
    private String expensesPaymentMethod;

    public MonthExpenses(LocalDate expensesDate, String expensesDescription, BigDecimal expensesAmount, String expensesCategory, String expensesPaymentMethod) {
        this.expensesDate = expensesDate;
        this.expensesDescription = expensesDescription;
        this.expensesAmount = expensesAmount;
        this.expensesCategory = expensesCategory;
        this.expensesPaymentMethod = expensesPaymentMethod;
    }

    public MonthExpenses() {}

    public LocalDate getExpensesDate() {
        return expensesDate;
    }

    public void setExpensesDate(LocalDate expensesDate) {
        this.expensesDate = expensesDate;
    }

    public String getExpensesDescription() {
        return expensesDescription;
    }

    public void setExpensesDescription(String expensesDescription) {
        this.expensesDescription = expensesDescription;
    }

    public BigDecimal getExpensesAmount() {
        return expensesAmount;
    }

    public void setExpensesAmount(BigDecimal expensesAmount) {
        this.expensesAmount = expensesAmount;
    }

    public String getExpensesCategory() {
        return expensesCategory;
    }

    public void setExpensesCategory(String expensesCategory) {
        this.expensesCategory = expensesCategory;
    }

    public String getExpensesPaymentMethod() {
        return expensesPaymentMethod;
    }

    public void setExpensesPaymentMethod(String expensesPaymentMethod) {
        this.expensesPaymentMethod = expensesPaymentMethod;
    }

    
}
