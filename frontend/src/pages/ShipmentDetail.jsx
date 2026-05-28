import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.js";
import { getSingleShipment } from "../api/shipmentApi.js";


function ShipmentDetail() {

    const { shipmentId } = useParams();
    const { user } = useAuth();

    const [shipmentData, setShipmentData] = useState(null);
    const [pageLoading, setPageLoading] = useState(true);
    const [fetchError, setFetchError] = useState("");


    useEffect(() => {
        loadShipment();
    }, [shipmentId]);


    
    async function loadShipment() {
        try {
            const result = await getSingleShipment(shipmentId);
            setShipmentData(result);

        } catch (err) {
            setFetchError(err.message);

        } finally {
            setPageLoading(false);
        }
    }



    if (pageLoading) {
        return (
            <div className="page">
                <p>Loading...</p>
            </div>
        );
    }



    if (fetchError) {
        return (
            <div className="page">
                <p className="error-message">{fetchError}</p>
                <Link className="button button-secondary" to="/shipments">Back</Link>
            </div>
        );
    }




    return (
        <div className="page">

            <div className="page-header">
                <h1>Shipment #{shipmentData.shipment_id}</h1>
            </div>

            <div className="content-card">

                <div className="detail-section">

                    <div className="detail-row">
                        <span className="detail-label">Shipment ID</span>
                        <span>{shipmentData.shipment_id}</span>
                    </div>



                    <div className="detail-row">
                        <span className="detail-label">Order ID</span>
                        <span>{shipmentData.order_id}</span>
                    </div>


                    <div className="detail-row">
                        <span className="detail-label">Recipient</span>
                        <span>{shipmentData.recipient_name}</span>
                    </div>


                    <div className="detail-row">
                        <span className="detail-label">Delivery Address</span>
                        <span>{shipmentData.delivery_address}</span>
                    </div>


                    <div className="detail-row">
                        <span className="detail-label">Status</span>
                        <span className="badge badge-purple">{shipmentData.status}</span>
                    </div>



                    <div className="detail-row">
                        <span className="detail-label">Created</span>
                        <span>{shipmentData.created_at}</span>
                    </div>


                    <div className="detail-row">
                        <span className="detail-label">Last Updated</span>
                        <span>{shipmentData.updated_at}</span>
                    </div>

                </div>

                <br />

                <div style={{ display: "flex", gap: "12px" }}>
                    {user?.role === "staff" && (
                        <Link className="button" to={`/shipments/${shipmentData.shipment_id}/edit`}>
                            Edit Shipment
                        </Link>
                    )}

                    <Link className="button button-secondary" to="/shipments">
                        Back to Shipments
                    </Link>
                </div>

            </div>

        </div>
    );
}


export default ShipmentDetail;
