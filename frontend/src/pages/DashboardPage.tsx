import { useAnalytics } from '../lib/queries'
import LoadingSpinner from '../components/LoadingSpinner'
import { Ticket, Layers, Clock, BookOpen, TrendingUp } from 'lucide-react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar, Doughnut } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend)

export default function DashboardPage() {
  const { data: analytics, isLoading } = useAnalytics()

  if (isLoading) {
    return <LoadingSpinner className="h-64" />
  }

  const stats = [
    { label: 'Total Tickets', value: analytics?.total_tickets || 0, icon: Ticket, color: 'bg-blue-500' },
    { label: 'Clusters', value: analytics?.total_clusters || 0, icon: Layers, color: 'bg-purple-500' },
    { label: 'Pending Approvals', value: analytics?.pending_approvals || 0, icon: Clock, color: 'bg-yellow-500' },
    { label: 'Knowledge Entries', value: analytics?.knowledge_entries || 0, icon: BookOpen, color: 'bg-green-500' },
  ]

  const categoryData = {
    labels: Object.keys(analytics?.tickets_by_category || {}),
    datasets: [
      {
        label: 'Tickets',
        data: Object.values(analytics?.tickets_by_category || {}),
        backgroundColor: ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'],
      },
    ],
  }

  const statusData = {
    labels: Object.keys(analytics?.clusters_by_status || {}),
    datasets: [
      {
        data: Object.values(analytics?.clusters_by_status || {}),
        backgroundColor: ['#fbbf24', '#3b82f6', '#22c55e', '#ef4444'],
      },
    ],
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <TrendingUp className="w-4 h-4" />
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="card">
            <div className="flex items-center gap-4">
              <div className={`${color} p-3 rounded-lg`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-gray-500">{label}</p>
                <p className="text-2xl font-bold">{value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Tickets by Category</h2>
          <div className="h-64">
            <Bar
              data={categoryData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
              }}
            />
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Clusters by Status</h2>
          <div className="h-64 flex items-center justify-center">
            <Doughnut
              data={statusData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
              }}
            />
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
        <div className="space-y-3">
          {analytics?.recent_activity?.length ? (
            analytics.recent_activity.map((item) => (
              <div key={item.id} className="flex items-center gap-3 py-2 border-b last:border-0">
                <div className="w-2 h-2 rounded-full bg-primary-500" />
                <p className="flex-1 text-sm">{item.description}</p>
                <span className="text-xs text-gray-500">
                  {new Date(item.timestamp).toLocaleString()}
                </span>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-sm">No recent activity</p>
          )}
        </div>
      </div>
    </div>
  )
}
