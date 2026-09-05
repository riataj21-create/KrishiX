import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Check } from 'lucide-react';
import { CROPS } from '../lib/mockData';
import { useToast } from '../context/ToastContext';
import { Eyebrow, Spinner } from '../components/ui/primitives';

const AddProducePage: React.FC = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [crop, setCrop] = useState('Tomato');
  const [variety, setVariety] = useState('');
  const [quantity, setQuantity] = useState('');
  const [harvestDate, setHarvestDate] = useState('');
  const [location, setLocation] = useState('');
  const [grade, setGrade] = useState('A');
  const [saving, setSaving] = useState(false);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    // Persisted via the backend once the produce endpoint is live.
    setTimeout(() => {
      setSaving(false);
      showToast(`${crop} added to your produce`, 'success');
      navigate('/produce');
    }, 700);
  };

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div>
        <Link to="/produce" className="mb-4 inline-flex items-center gap-1.5 text-sm" style={{ color: 'var(--text-secondary)' }}>
          <ArrowLeft size={16} /> Back to My Produce
        </Link>
        <Eyebrow>New listing</Eyebrow>
        <h1 className="text-h1 font-display mt-2">Add produce</h1>
        <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
          The more accurate the detail, the sharper the buyer match.
        </p>
      </div>

      <form onSubmit={submit} className="card space-y-6 p-6 md:p-8">
        <div className="grid gap-5 sm:grid-cols-2">
          <div>
            <label className="mb-1.5 block text-sm font-medium" htmlFor="crop">Crop</label>
            <select id="crop" className="select" value={crop} onChange={(e) => setCrop(e.target.value)}>
              {CROPS.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium" htmlFor="variety">Variety</label>
            <input
              id="variety"
              className="input"
              placeholder="e.g. Hybrid, Guntur"
              value={variety}
              onChange={(e) => setVariety(e.target.value)}
            />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium" htmlFor="quantity">Quantity (quintal)</label>
            <input
              id="quantity"
              type="number"
              min="1"
              required
              className="input"
              placeholder="e.g. 60"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
            />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium" htmlFor="grade">Grade</label>
            <select id="grade" className="select" value={grade} onChange={(e) => setGrade(e.target.value)}>
              <option value="A">Grade A — premium</option>
              <option value="B">Grade B — standard</option>
              <option value="C">Grade C — ordinary</option>
            </select>
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium" htmlFor="harvest">Harvest date</label>
            <input
              id="harvest"
              type="date"
              required
              className="input"
              value={harvestDate}
              onChange={(e) => setHarvestDate(e.target.value)}
            />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium" htmlFor="location">Location</label>
            <input
              id="location"
              required
              className="input"
              placeholder="Village, District"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            />
          </div>
        </div>

        <div className="flex items-center justify-end gap-3 border-t pt-6" style={{ borderColor: 'var(--border)' }}>
          <Link to="/produce" className="btn btn-ghost">Cancel</Link>
          <button type="submit" disabled={saving} className="btn btn-primary">
            {saving ? <Spinner /> : <><Check size={18} /> Save produce</>}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AddProducePage;
