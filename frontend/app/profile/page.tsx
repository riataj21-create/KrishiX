/**
 * Farmer Profile & Settings Page
 * Manage personal information and preferences
 */

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, Loader2, CheckCircle } from "lucide-react";
import { farmerProfileAPI } from "@/lib/api";

export default function ProfilePage() {
  const router = useRouter();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");
  const [isNewProfile, setIsNewProfile] = useState(false);

  const [formData, setFormData] = useState({
    full_name: "",
    phone: "",
    state: "",
    district: "",
    village: "",
    postal_code: "",
    latitude: "",
    longitude: "",
    bio: "",
  });

  // Check auth
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/auth/login");
    }
  }, [router]);

  // Load profile
  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      setError("");
      const response = await farmerProfileAPI.getProfile();
      setFormData({
        full_name: response.full_name || "",
        phone: response.phone || "",
        state: response.state || "",
        district: response.district || "",
        village: response.village || "",
        postal_code: response.postal_code || "",
        latitude: response.latitude || "",
        longitude: response.longitude || "",
        bio: response.bio || "",
      });
    } catch (err: any) {
      if (err.message.includes("404")) {
        // Profile doesn't exist yet — form stays empty, we'll POST on save
        setIsNewProfile(true);
        setError("");
      } else {
        setError("Failed to load profile");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.full_name || !formData.state || !formData.district) {
      setError("Name, state, and district are required");
      return;
    }

    try {
      setSaving(true);
      setError("");
      setSuccess("");

      if (isNewProfile) {
        await farmerProfileAPI.createProfile(formData);
        setIsNewProfile(false);
      } else {
        await farmerProfileAPI.updateProfile(formData);
      }
      
      setSuccess("Profile updated successfully!");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err: any) {
      setError("Failed to update profile");
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center">
          <Loader2 className="w-8 h-8 animate-spin text-primary mb-4" />
          <p className="text-neutral-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <section className="bg-white border-b border-neutral-200">
        <div className="mx-auto max-w-4xl px-6 py-8">
          <h1 className="text-h3 mb-2">Profile Settings</h1>
          <p className="text-neutral-600">
            Update your personal information and preferences
          </p>
        </div>
      </section>

      {/* Main Content */}
      <section className="mx-auto max-w-4xl px-6 py-12">
        {error && (
          <div className="bg-danger/10 border border-danger/30 text-danger px-4 py-3 rounded-lg flex gap-3 mb-6">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <p>{error}</p>
          </div>
        )}

        {success && (
          <div className="bg-success/10 border border-success/30 text-success px-4 py-3 rounded-lg flex gap-3 mb-6">
            <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <p>{success}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="card">
          <div className="card-body space-y-6">
            {/* Personal Information */}
            <div>
              <h3 className="text-h5 mb-4">Personal Information</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    name="full_name"
                    className="input"
                    placeholder="Your full name"
                    value={formData.full_name}
                    onChange={handleChange}
                    disabled={saving}
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    className="input"
                    placeholder="+91 XXXXX XXXXX"
                    value={formData.phone}
                    onChange={handleChange}
                    disabled={saving}
                  />
                </div>
              </div>
            </div>

            {/* Location Information */}
            <div className="pt-4 border-t border-neutral-200">
              <h3 className="text-h5 mb-4">Location Information</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    State *
                  </label>
                  <select
                    name="state"
                    className="input"
                    value={formData.state}
                    onChange={handleChange}
                    disabled={saving}
                    required
                  >
                    <option value="">Select state</option>
                    <option value="Punjab">Punjab</option>
                    <option value="Maharashtra">Maharashtra</option>
                    <option value="Haryana">Haryana</option>
                    <option value="Uttar Pradesh">Uttar Pradesh</option>
                    <option value="Karnataka">Karnataka</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    District *
                  </label>
                  <input
                    type="text"
                    name="district"
                    className="input"
                    placeholder="District name"
                    value={formData.district}
                    onChange={handleChange}
                    disabled={saving}
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Village
                  </label>
                  <input
                    type="text"
                    name="village"
                    className="input"
                    placeholder="Village name"
                    value={formData.village}
                    onChange={handleChange}
                    disabled={saving}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Postal Code
                  </label>
                  <input
                    type="text"
                    name="postal_code"
                    className="input"
                    placeholder="Postal code"
                    value={formData.postal_code}
                    onChange={handleChange}
                    disabled={saving}
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4 mt-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Latitude (Optional)
                  </label>
                  <input
                    type="number"
                    step="0.0001"
                    name="latitude"
                    className="input"
                    placeholder="e.g., 31.1234"
                    value={formData.latitude}
                    onChange={handleChange}
                    disabled={saving}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Longitude (Optional)
                  </label>
                  <input
                    type="number"
                    step="0.0001"
                    name="longitude"
                    className="input"
                    placeholder="e.g., 75.5678"
                    value={formData.longitude}
                    onChange={handleChange}
                    disabled={saving}
                  />
                </div>
              </div>
            </div>

            {/* Additional Information */}
            <div className="pt-4 border-t border-neutral-200">
              <h3 className="text-h5 mb-4">About You</h3>
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Bio
                </label>
                <textarea
                  name="bio"
                  className="input"
                  placeholder="Tell us about yourself (optional)"
                  rows={4}
                  value={formData.bio}
                  onChange={handleChange}
                  disabled={saving}
                />
                <p className="text-xs text-neutral-500 mt-2">
                  This information helps other farmers understand your farming practices
                </p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="card-footer flex gap-4">
            <button
              type="submit"
              className="btn-primary"
              disabled={saving}
            >
              {saving ? (
                <>
                  <Loader2 className="mr-2 w-4 h-4 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save Changes"
              )}
            </button>
            <a href="/dashboard" className="btn-outline">
              Back to Dashboard
            </a>
          </div>
        </form>

        {/* Help Section */}
        <div className="mt-8 bg-neutral-100 rounded-lg p-6 border border-neutral-200">
          <h4 className="font-semibold text-neutral-900 mb-2">Why we need this info?</h4>
          <p className="text-sm text-neutral-700">
            Your profile helps us provide better market recommendations. Your location is used to show prices from nearby APMC markets. All information is private and never shared with third parties.
          </p>
        </div>
      </section>
    </div>
  );
}
