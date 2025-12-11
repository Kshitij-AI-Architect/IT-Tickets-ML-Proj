interface StatusBadgeProps {
  status: string
}

const statusConfig: Record<string, { className: string; label: string }> = {
  pending: { className: 'badge-warning', label: 'Pending' },
  reviewed: { className: 'badge-info', label: 'Reviewed' },
  approved: { className: 'badge-success', label: 'Approved' },
  rejected: { className: 'badge-error', label: 'Rejected' },
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status] || { className: 'badge-info', label: status }
  return <span className={config.className}>{config.label}</span>
}
