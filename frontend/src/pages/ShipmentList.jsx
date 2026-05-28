import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.js";
import { getMyShipments } from "../api/shipmentApi.js";


function ShipmentList() {

    const { user } = useAuth();

    const [allShipments, setAllShipments] = useState([]);
    const [pageLoading, setPageLoading] = useState(true);
    const [fetchError, setFetchError] = useState("");


    useEffect(() => {
        loadShipments();
    }, []);



    async function loadShipments() {
        try {
            const result = await getMyShipments();
            setAllShipments(result);

        } catch (err) {
            setFetchError(err.message);

        } finally {
            setPageLoading(false);
        }
    }




    function renderStatusBadge(status) {
        if (status === "delivered") {
            return <span className="badge badge-blue">{status}</span>;
        }
        return <span className="badge badge-purple">{status}</span>;
    }




    if (pageLoading) {
        return (
            <div className="page">
                <p>Loading shipments...</p>
            </div>
        );
    }

    

    
    return (
        <div className="page">

            <div className="page-header">
                <h1>Shipments</h1>

                {user?.role === "staff" && (
                    <Link className="button" to="/shipments/create">+ New Shipment</Link>
                )}
            </div>

            {fetchError && <p className="error-message">{fetchError}</p>}

            <div className="content-card">

                {allShipments.length === 0 ? (

                    <p>No shipments found.</p>

                ) : (

                    <div className="table-wrapper">
                        <table className="access-log-table">
                            <thead>
                                <tr>
                                    <th>Shipment #</th>
                                    <th>Order #</th>
                                    <th>Recipient</th>
                                    <th>Status</th>
                                    <th>Created</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>

                            <tbody>
                                {allShipments.map((shipment) => (
                                    <tr key={shipment.shipment_id}>
                                        <td>{shipment.shipment_id}</td>
                                        <td>{shipment.order_id}</td>
                                        <td>{shipment.recipient_name}</td>
                                        <td>{renderStatusBadge(shipment.status)}</td>
                                        <td>{shipment.created_at}</td>
                                        <td>
                                            <Link
                                                className="button button-secondary"
                                                to={`/shipments/${shipment.shipment_id}`}
                                            >
                                                View
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                )}

            </div>

        </div>
    );
}


export default ShipmentList;
