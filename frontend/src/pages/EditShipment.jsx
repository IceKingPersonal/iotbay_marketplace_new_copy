import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getSingleShipment, updateShipment } from "../api/shipmentApi.js";


function EditShipment() {

    const { shipmentId } = useParams();
    const navigate = useNavigate();

    const [selectedStatus, setSelectedStatus] = useState("");
    const [recipientInput, setRecipientInput] = useState("");
    const [addressInput, setAddressInput] = useState("");
    const [pageLoading, setPageLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitError, setSubmitError] = useState("");
    const [submitSuccess, setSubmitSuccess] = useState("");

    const validStatuses = ["pending", "shipped", "delivered"];


    useEffect(() => {
        loadCurrentShipment();
    }, [shipmentId]);




    async function loadCurrentShipment() {
        try {
            const result = await getSingleShipment(shipmentId);

            setSelectedStatus(result.status);
            setRecipientInput(result.recipient_name);
            setAddressInput(result.delivery_address);

        } catch (err) {
            setSubmitError(err.message);

        } finally {
            setPageLoading(false);
        }
    }


    

    async function handleSave() {
        setSubmitError("");
        setSubmitSuccess("");

        if (!recipientInput.trim() || !addressInput.trim()) {
            setSubmitError("Recipient name and delivery address are required.");
            return;
        }

        setIsSubmitting(true);

        try {
            await updateShipment(shipmentId, selectedStatus, recipientInput.trim(), addressInput.trim());

            setSubmitSuccess("Shipment updated successfully.");

            setTimeout(() => {
                navigate(`/shipments/${shipmentId}`);
            }, 1000);

        } catch (err) {
            setSubmitError(err.message);

        } finally {
            setIsSubmitting(false);
        }
    }



    if (pageLoading) {
        return (
            <div className="page">
                <p>Loading...</p>
            </div>
        );
    }



    return (
        <div className="page">

            <div className="page-header">
                <h1>Edit Shipment #{shipmentId}</h1>
            </div>

            <div className="content-card">

                {submitError && <p className="error-message">{submitError}</p>}
                {submitSuccess && <p className="success-message">{submitSuccess}</p>}

                <div style={{ marginBottom: "16px" }}>
                    <label>Status</label>
                    <select
                        value={selectedStatus}
                        onChange={(e) => setSelectedStatus(e.target.value)}
                    >
                        {validStatuses.map((s) => (
                            <option key={s} value={s}>
                                {s.charAt(0).toUpperCase() + s.slice(1)}
                            </option>
                        ))}
                    </select>
                </div>



                <div style={{ marginBottom: "16px" }}>
                    <label>Recipient Name</label>
                    <input
                        type="text"
                        value={recipientInput}
                        onChange={(e) => setRecipientInput(e.target.value)}
                    />
                </div>


                <div style={{ marginBottom: "24px" }}>
                    <label>Delivery Address</label>
                    <input
                        type="text"
                        value={addressInput}
                        onChange={(e) => setAddressInput(e.target.value)}
                    />
                </div>


                <div style={{ display: "flex", gap: "12px" }}>

                    <button onClick={handleSave} disabled={isSubmitting}>
                        {isSubmitting ? "Saving..." : "Save Changes"}
                    </button>

                    <button
                        className="button-secondary"
                        onClick={() => navigate(`/shipments/${shipmentId}`)}
                    >
                        Cancel
                    </button>

                </div>

            </div>

        </div>
    );
}


export default EditShipment;
