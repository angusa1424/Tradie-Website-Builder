import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { createWebsite } from '../services/api';
import '../styles/WebsiteBuilder.css';

const WebsiteBuilder = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [websiteData, setWebsiteData] = useState({
    businessName: '',
    phone: '',
    email: '',
    address: '',
    services: [],
    businessHours: {
      monday: { open: '8:00', close: '17:00' },
      tuesday: { open: '8:00', close: '17:00' },
      wednesday: { open: '8:00', close: '17:00' },
      thursday: { open: '8:00', close: '17:00' },
      friday: { open: '8:00', close: '17:00' },
      saturday: { open: '9:00', close: '14:00' },
      sunday: { open: 'Closed', close: 'Closed' }
    },
    location: '',
    template: 'tradie-1'
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setWebsiteData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleServiceAdd = (e) => {
    e.preventDefault();
    const service = e.target.service.value;
    if (service && !websiteData.services.includes(service)) {
      setWebsiteData(prev => ({
        ...prev,
        services: [...prev.services, service]
      }));
      e.target.service.value = '';
    }
  };

  const handleServiceRemove = (service) => {
    setWebsiteData(prev => ({
      ...prev,
      services: prev.services.filter(s => s !== service)
    }));
  };

  const handleBusinessHoursChange = (day, field, value) => {
    setWebsiteData(prev => ({
      ...prev,
      businessHours: {
        ...prev.businessHours,
        [day]: {
          ...prev.businessHours[day],
          [field]: value
        }
      }
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await createWebsite({
        ...websiteData,
        userId: user.id
      });
      
      navigate(`/dashboard/websites/${response.id}`);
    } catch (err) {
      setError(err.message || 'Failed to create website');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="website-builder">
      <div className="builder-header">
        <h1>Create Your Tradie Website in 3 Steps</h1>
        <div className="progress-bar">
          <div className={`progress-step ${step >= 1 ? 'active' : ''}`}>1. Business Info</div>
          <div className={`progress-step ${step >= 2 ? 'active' : ''}`}>2. Services</div>
          <div className={`progress-step ${step >= 3 ? 'active' : ''}`}>3. Review & Create</div>
        </div>
      </div>

      <div className="builder-content">
        {step === 1 && (
          <div className="step-content">
            <h2>Step 1: Business Information</h2>
            <form onSubmit={(e) => { e.preventDefault(); setStep(2); }}>
              <div className="form-group">
                <label>Business Name</label>
                <input
                  type="text"
                  name="businessName"
                  value={websiteData.businessName}
                  onChange={handleInputChange}
                  required
                />
              </div>
              
              <div className="form-group">
                <label>Phone Number</label>
                <input
                  type="tel"
                  name="phone"
                  value={websiteData.phone}
                  onChange={handleInputChange}
                  required
                />
              </div>
              
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  name="email"
                  value={websiteData.email}
                  onChange={handleInputChange}
                  required
                />
              </div>
              
              <div className="form-group">
                <label>Address</label>
                <textarea
                  name="address"
                  value={websiteData.address}
                  onChange={handleInputChange}
                  required
                />
              </div>
              
              <div className="form-group">
                <label>Location (City/Suburb)</label>
                <input
                  type="text"
                  name="location"
                  value={websiteData.location}
                  onChange={handleInputChange}
                  required
                />
              </div>
              
              <button type="submit" className="btn-next">Next Step</button>
            </form>
          </div>
        )}

        {step === 2 && (
          <div className="step-content">
            <h2>Step 2: Services & Hours</h2>
            <form onSubmit={handleServiceAdd}>
              <div className="form-group">
                <label>Add Service</label>
                <div className="service-input">
                  <input
                    type="text"
                    name="service"
                    placeholder="e.g., Plumbing, Electrical, Carpentry"
                  />
                  <button type="submit">Add</button>
                </div>
              </div>
            </form>

            <div className="services-list">
              {websiteData.services.map(service => (
                <div key={service} className="service-item">
                  {service}
                  <button onClick={() => handleServiceRemove(service)}>×</button>
                </div>
              ))}
            </div>

            <div className="business-hours">
              <h3>Business Hours</h3>
              {Object.entries(websiteData.businessHours).map(([day, hours]) => (
                <div key={day} className="hours-row">
                  <label>{day.charAt(0).toUpperCase() + day.slice(1)}</label>
                  <input
                    type="text"
                    value={hours.open}
                    onChange={(e) => handleBusinessHoursChange(day, 'open', e.target.value)}
                  />
                  <span>to</span>
                  <input
                    type="text"
                    value={hours.close}
                    onChange={(e) => handleBusinessHoursChange(day, 'close', e.target.value)}
                  />
                </div>
              ))}
            </div>

            <div className="button-group">
              <button onClick={() => setStep(1)} className="btn-back">Back</button>
              <button onClick={() => setStep(3)} className="btn-next">Next Step</button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="step-content">
            <h2>Step 3: Review & Create</h2>
            <div className="review-section">
              <h3>Business Information</h3>
              <p><strong>Name:</strong> {websiteData.businessName}</p>
              <p><strong>Phone:</strong> {websiteData.phone}</p>
              <p><strong>Email:</strong> {websiteData.email}</p>
              <p><strong>Address:</strong> {websiteData.address}</p>
              <p><strong>Location:</strong> {websiteData.location}</p>
            </div>

            <div className="review-section">
              <h3>Services</h3>
              <ul>
                {websiteData.services.map(service => (
                  <li key={service}>{service}</li>
                ))}
              </ul>
            </div>

            <div className="review-section">
              <h3>Business Hours</h3>
              {Object.entries(websiteData.businessHours).map(([day, hours]) => (
                <p key={day}>
                  <strong>{day.charAt(0).toUpperCase() + day.slice(1)}:</strong> {hours.open} - {hours.close}
                </p>
              ))}
            </div>

            <div className="pricing-info">
              <h3>Pricing</h3>
              <p>One-time setup fee: $299.95</p>
              <p>Monthly hosting: $29.95</p>
            </div>

            <div className="button-group">
              <button onClick={() => setStep(2)} className="btn-back">Back</button>
              <button 
                onClick={handleSubmit} 
                className="btn-create"
                disabled={isLoading}
              >
                {isLoading ? 'Creating...' : 'Create Website'}
              </button>
            </div>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default WebsiteBuilder; 