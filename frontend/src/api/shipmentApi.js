import { apiRequest } from "./apiClient";




export async function getMyShipments() {
    const response = await apiRequest("/shipments/");
    return response.shipments;
}




export async function getSingleShipment(shipmentId) {
    const response = await apiRequest(`/shipments/${shipmentId}`);
    return response.shipment;
}




export async function createShipment(orderId, deliveryAddress) {
    const response = await apiRequest("/shipments/", {
        method: "POST",
        body: JSON.stringify({
            order_id: orderId,
            delivery_address: deliveryAddress
        })
    });

    return response.shipment;
}




export async function updateShipment(shipmentId, newStatus, recipientName, deliveryAddress) {
    const response = await apiRequest(`/shipments/${shipmentId}`, {
        method: "PUT",
        body: JSON.stringify({
            status: newStatus,
            recipient_name: recipientName,
            delivery_address: deliveryAddress
        })
    });

    return response.shipment;
}
