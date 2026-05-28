// Feature 03 — Create order (customer)
import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiRequest } from "../api/apiClient.js";
import { createOrder } from "../api/orders.js";
import { useAuth } from "../hooks/useAuth.js";

function formatMoney(cents) {
  return (cents / 100).toFixed(2);
}

function priceToCents(dollars) {
  return Math.round(Number(dollars) * 100);
}

function CreateOrder() {
  const navigate = useNavigate();
  const { user, isLoggedIn, loading: authLoading } = useAuth();
  const isCustomer = user?.role === "customer";

  const [products, setProducts] = useState([]);
  const [orderLines, setOrderLines] = useState([]);
  const [shippingAddress, setShippingAddress] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const [modalOpen, setModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedProductId, setSelectedProductId] = useState(null);
  const [modalQuantity, setModalQuantity] = useState(1);
  const [modalError, setModalError] = useState("");

  useEffect(() => {
    if (authLoading || !isLoggedIn || !isCustomer) {
      return;
    }

    setShippingAddress(user?.address || "");

    async function loadProducts() {
      setLoading(true);
      setError("");

      try {
        const data = await apiRequest("/devices?in_stock=true");
        setProducts(data.devices);
      } catch (err) {
        setError(err.message);
        setProducts([]);
      } finally {
        setLoading(false);
      }
    }

    loadProducts();
  }, [authLoading, isCustomer, isLoggedIn, user?.address]);

  function getLineQuantity(productId) {
    return orderLines.find((line) => line.product_id === productId)?.quantity || 0;
  }

  function getRemainingStock(product) {
    return product.stock_quantity - getLineQuantity(product.device_id);
  }

  const filteredProducts = useMemo(() => {
    const query = searchTerm.trim().toLowerCase();

    return products.filter((product) => {
      if (getRemainingStock(product) < 1) {
        return false;
      }

      if (!query) {
        return true;
      }

      const haystack = [
        product.name,
        product.brand,
        product.category,
        product.model,
        product.description,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return haystack.includes(query);
    });
  }, [products, searchTerm, orderLines]);

  const selectedProduct = products.find(
    (product) => product.device_id === selectedProductId
  );

  const estimatedTotalCents = useMemo(() => {
    return orderLines.reduce((total, line) => {
      return total + priceToCents(line.product.price) * line.quantity;
    }, 0);
  }, [orderLines]);

  function openModal() {
    setModalOpen(true);
    setSearchTerm("");
    setSelectedProductId(null);
    setModalQuantity(1);
    setModalError("");
  }

  function closeModal() {
    setModalOpen(false);
    setModalError("");
  }

  function handleAddLine() {
    if (!selectedProduct) {
      setModalError("Select a device to add.");
      return;
    }

    const remainingStock = getRemainingStock(selectedProduct);
    const quantity = Number.parseInt(String(modalQuantity), 10);

    if (!Number.isInteger(quantity) || quantity < 1) {
      setModalError("Quantity must be at least 1.");
      return;
    }

    if (quantity > remainingStock) {
      setModalError(`Only ${remainingStock} available in stock.`);
      return;
    }

    setOrderLines((current) => {
      const existing = current.find(
        (line) => line.product_id === selectedProduct.device_id
      );

      if (existing) {
        return current.map((line) =>
          line.product_id === selectedProduct.device_id
            ? { ...line, quantity: line.quantity + quantity }
            : line
        );
      }

      return [
        ...current,
        {
          product_id: selectedProduct.device_id,
          quantity,
          product: selectedProduct,
        },
      ];
    });

    closeModal();
  }

  function removeLine(productId) {
    setOrderLines((current) =>
      current.filter((line) => line.product_id !== productId)
    );
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    const address = shippingAddress.trim();
    if (!address) {
      setError("Shipping address is required.");
      return;
    }

    if (orderLines.length === 0) {
      setError("Add at least one device to your order.");
      return;
    }

    setSubmitting(true);

    try {
      const payload = await createOrder({
        shipping_address: address,
        currency: "AUD",
        items: orderLines.map(({ product_id, quantity }) => ({
          product_id,
          quantity,
        })),
      });

      navigate(`/orders/${payload.order.order_id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  if (authLoading) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>Create order</h1>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isLoggedIn) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>Create order</h1>
          <p>You must be logged in to place an order.</p>
        </div>
      </div>
    );
  }

  if (!isCustomer) {
    return (
      <div className="page">
        <div className="page-header page-header-centered">
          <h1>Create order</h1>
          <p>Only customer accounts can create orders.</p>
          <Link className="btn btn-secondary" to="/orders">
            Back to orders
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header page-header-centered">
        <h1>Create order</h1>
        <p>Add devices to your order, then place it as Saved.</p>
        <p className="muted">
          <Link to="/orders">Back to my orders</Link>
        </p>
      </div>

      <form className="card form" onSubmit={handleSubmit}>
        <h2>Shipping</h2>
        <label className="field">
          <span>Shipping address</span>
          <textarea
            value={shippingAddress}
            onChange={(event) => setShippingAddress(event.target.value)}
            rows={3}
            required
          />
        </label>

        <div className="order-lines-header">
          <h2>Devices</h2>
          <button
            type="button"
            className="btn-add-device"
            onClick={openModal}
            disabled={loading || products.length === 0}
            aria-label="Add device"
            title="Add device"
          >
            +
          </button>
        </div>

        {loading ? <p>Loading available devices...</p> : null}

        {!loading && products.length === 0 ? (
          <p className="muted">No in-stock devices are available right now.</p>
        ) : null}

        {orderLines.length === 0 && !loading ? (
          <p className="muted">Click + to add a device to this order.</p>
        ) : null}

        {orderLines.length > 0 ? (
          <ul className="product-list">
            {orderLines.map((line) => (
              <li key={line.product_id} className="card product-card">
                <div>
                  <strong>{line.product.name}</strong>
                  <div className="muted">
                    {[line.product.brand, line.product.category]
                      .filter(Boolean)
                      .join(" · ")}
                  </div>
                  <div className="muted">
                    ${Number(line.product.price).toFixed(2)} · Qty {line.quantity}
                  </div>
                </div>
                <div className="product-meta">
                  <span>
                    ${formatMoney(priceToCents(line.product.price) * line.quantity)}
                  </span>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => removeLine(line.product_id)}
                  >
                    Remove
                  </button>
                </div>
              </li>
            ))}
          </ul>
        ) : null}

        <div className="order-summary">
          <strong>Estimated total:</strong> ${formatMoney(estimatedTotalCents)} AUD
        </div>

        {error ? <p className="form-error">{error}</p> : null}

        <div className="form-actions">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting || orderLines.length === 0}
          >
            {submitting ? "Placing order..." : "Place order"}
          </button>
        </div>
      </form>

      {modalOpen ? (
        <div className="modal-overlay" onClick={closeModal}>
          <div
            className="modal-card card form"
            onClick={(event) => event.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-labelledby="add-device-title"
          >
            <h2 id="add-device-title">Add device</h2>

            <label className="field">
              <span>Search devices</span>
              <input
                type="search"
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
                placeholder="Name, brand, type, or model"
                autoFocus
              />
            </label>

            <div className="modal-product-list">
              {filteredProducts.length === 0 ? (
                <p className="muted">No matching in-stock devices found.</p>
              ) : (
                filteredProducts.map((product) => {
                  const isSelected = selectedProductId === product.device_id;

                  return (
                    <button
                      key={product.device_id}
                      type="button"
                      className={`modal-product-option${
                        isSelected ? " modal-product-option--selected" : ""
                      }`}
                      onClick={() => {
                        setSelectedProductId(product.device_id);
                        setModalQuantity(1);
                        setModalError("");
                      }}
                    >
                      <strong>{product.name}</strong>
                      <span className="muted">
                        {[product.brand, product.category]
                          .filter(Boolean)
                          .join(" · ")}
                      </span>
                      <span className="muted">
                        ${Number(product.price).toFixed(2)} ·{" "}
                        {getRemainingStock(product)} available
                      </span>
                    </button>
                  );
                })
              )}
            </div>

            <label className="field">
              <span>Quantity</span>
              <input
                type="number"
                min="1"
                max={selectedProduct ? getRemainingStock(selectedProduct) : 1}
                value={modalQuantity}
                onChange={(event) => setModalQuantity(event.target.value)}
                disabled={!selectedProduct}
              />
            </label>

            {modalError ? <p className="form-error">{modalError}</p> : null}

            <div className="form-actions">
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleAddLine}
              >
                Add
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={closeModal}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export default CreateOrder;
