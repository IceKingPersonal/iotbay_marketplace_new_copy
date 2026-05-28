import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createShipment } from "../api/shipmentApi.js";


function CreateShipment() {

    const navigate = useNavigate();

    const [enteredOrderId, setEnteredOrderId] = useState("");
    const [enteredAddress, setEnteredAddress] = useState("");
    const [submitError, setSubmitError] = useState("");
    const [submitSuccess, setSubmitSuccess] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);

    

    async function handleCreate() {
        setSubmitError("");
        setSubmitSuccess("");

        if (!enteredOrderId || !enteredAddress.trim()) {
            setSubmitError("Please fill in all fields.");
            return;
        }

        setIsSubmitting(true);

        try {
            const createdShipment = await createShipment(Number(enteredOrderId), enteredAddress.trim());

            setSubmitSuccess("Shipment created successfully.");

            setTimeout(() => {
                navigate(`/shipments/${createdShipment.shipment_id}`);
            }, 1000);

        } catch (err) {
            setSubmitError(err.message);

        } finally {
            setIsSubmitting(false);
        }
    }




    return (
        <div className="page">

            <div className="page-header">
                <h1>Create Shipment</h1>
                <p>You can only create a shipment for an order that has been paid.</p>
            </div>

            <div className="content-card">

                {submitError && <p className="error-message">{submitError}</p>}
                {submitSuccess && <p className="success-message">{submitSuccess}</p>}

                <div style={{ marginBottom: "16px" }}>
                    <label>Order ID</label>
                    <input
                        type="number"
                        value={enteredOrderId}
                        onChange={(e) => setEnteredOrderId(e.target.value)}
                        placeholder="e.g. 3"
                        min="1"
                    />
                </div>

                <div style={{ marginBottom: "24px" }}>
                    <label>Delivery Address</label>
                    <input
                        type="text"
                        value={enteredAddress}
                        onChange={(e) => setEnteredAddress(e.target.value)}
                        placeholder="Street, Suburb, State, Postcode"
                    />
                </div>

                <div style={{ display: "flex", gap: "12px" }}>

                    <button onClick={handleCreate} disabled={isSubmitting}>
                        {isSubmitting ? "Creating..." : "Create Shipment"}
                    </button>

                    <button className="button-secondary" onClick={() => navigate("/shipments")}>
                        Cancel
                    </button>

                </div>

            </div>

        </div>
    );
}


export default CreateShipment;
