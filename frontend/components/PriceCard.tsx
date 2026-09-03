/**
 * Price Card Component
 * Displays commodity price with optional save action
 */

import { Bookmark, BookmarkCheck, TrendingDown, TrendingUp } from "lucide-react";

interface PriceCardProps {
  commodityName: string;
  marketName: string;
  price: number;
  minPrice: number;
  maxPrice: number;
  change?: number;
  lastUpdated: string;
  // Optional save/unsave
  commodityId?: string;
  marketId?: string;
  saved?: boolean;
  onSave?: (commodityId: string) => void;
  onUnsave?: (commodityId: string) => void;
}

export default function PriceCard({
  commodityName,
  marketName,
  price,
  minPrice,
  maxPrice,
  change,
  lastUpdated,
  commodityId,
  saved,
  onSave,
  onUnsave,
}: PriceCardProps) {
  const isPositive = change ? change >= 0 : false;
  const canSave = !!(commodityId && (onSave || onUnsave));

  function handleSaveClick(e: React.MouseEvent) {
    e.preventDefault();
    if (!commodityId) return;
    if (saved) {
      onUnsave?.(commodityId);
    } else {
      onSave?.(commodityId);
    }
  }

  return (
    <div className="card">
      <div className="card-body">
        {/* Header */}
        <div className="mb-4 flex items-start justify-between">
          <div className="min-w-0 flex-1">
            <h3 className="text-h6 text-neutral-900">{commodityName}</h3>
            <p className="text-sm text-neutral-600">{marketName}</p>
          </div>
          <div className="ml-2 flex items-center gap-2">
            {change !== undefined && (
              <div className={`flex items-center gap-1 ${isPositive ? "text-success" : "text-danger"}`}>
                {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                <span className="text-sm font-medium">
                  {isPositive ? "+" : ""}{change.toFixed(2)}%
                </span>
              </div>
            )}
            {canSave && (
              <button
                onClick={handleSaveClick}
                aria-label={saved ? `Remove ${commodityName} from saved` : `Save ${commodityName}`}
                title={saved ? "Remove from saved" : "Save commodity"}
                className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded transition-colors ${
                  saved
                    ? "text-[var(--accent)] hover:text-[var(--error)]"
                    : "text-[var(--text-muted)] hover:text-[var(--accent)]"
                }`}
              >
                {saved ? <BookmarkCheck size={18} /> : <Bookmark size={18} />}
              </button>
            )}
          </div>
        </div>

        {/* Price */}
        <div className="mb-4">
          <p className="text-xs text-neutral-500 uppercase tracking-wider mb-1">Modal Price</p>
          <p className="text-3xl font-semibold tracking-tight text-[var(--text-primary)]">
            ₹{price.toLocaleString()}
            <span className="ml-1 text-sm font-normal text-[var(--text-secondary)]">/ quintal</span>
          </p>
        </div>

        {/* Price Range */}
        <div className="grid grid-cols-2 gap-4 border-y border-[var(--border)] py-3 mb-4">
          <div>
            <p className="text-xs text-neutral-600 mb-1">Min Price</p>
            <p className="font-semibold text-neutral-900">₹{minPrice.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-xs text-neutral-600 mb-1">Max Price</p>
            <p className="font-semibold text-neutral-900">₹{maxPrice.toLocaleString()}</p>
          </div>
        </div>

        {/* Last Updated */}
        <p className="text-xs text-neutral-500">Last updated: {lastUpdated}</p>
      </div>
    </div>
  );
}
