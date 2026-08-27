import java.math.BigDecimal;

import main.java.ms_ingestion_data.msIngestionData.enums.EMERGENCY_TYPE;

public class EmergencySavingFund {

    private EMERGENCY_TYPE emergencyTapy;
    private BigDecimal emergencyAmount;
    
    
    public EmergencySavingFund(EMERGENCY_TYPE emergencyTapy, BigDecimal emergencyAmount) {
        this.emergencyTapy = emergencyTapy;
        this.emergencyAmount = emergencyAmount;
    }


    public EMERGENCY_TYPE getEmergencyTapy() {
        return emergencyTapy;
    }


    public void setEmergencyTapy(EMERGENCY_TYPE emergencyTapy) {
        this.emergencyTapy = emergencyTapy;
    }


    public BigDecimal getEmergencyAmount() {
        return emergencyAmount;
    }


    public void setEmergencyAmount(BigDecimal emergencyAmount) {
        this.emergencyAmount = emergencyAmount;
    }

    

}