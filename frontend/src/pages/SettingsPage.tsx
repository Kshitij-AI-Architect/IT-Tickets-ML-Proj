import { useState } from 'react'
import { useAuthStore } from '../stores/authStore'
import { User, Building, Key, Bell } from 'lucide-react'
import toast from 'react-hot-toast'

export default function SettingsPage() {
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState('profile')

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'organization', label: 'Organization', icon: Building },
    { id: 'api', label: 'API Keys', icon: Key },
    { id: 'notifications', label: 'Notifications', icon: Bell },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Tabs */}
        <div className="lg:w-48 flex lg:flex-col gap-1">
          {tabs.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-left transition-colors ${
                activeTab === id
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1">
          {activeTab === 'profile' && <ProfileSettings user={user} />}
          {activeTab === 'organization' && <OrganizationSettings />}
          {activeTab === 'api' && <ApiSettings />}
          {activeTab === 'notifications' && <NotificationSettings />}
        </div>
      </div>
    </div>
  )
}

function ProfileSettings({ user }: { user: { name?: string; email?: string; role?: string } | null }) {
  const [name, setName] = useState(user?.name || '')
  const [email, setEmail] = useState(user?.email || '')

  const handleSave = () => {
    toast.success('Profile updated')
  }

  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">Profile Settings</h2>
      <div className="space-y-4 max-w-md">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="input"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
          <input
            type="text"
            value={user?.role || ''}
            disabled
            className="input bg-gray-50"
          />
        </div>
        <button onClick={handleSave} className="btn-primary">
          Save Changes
        </button>
      </div>
    </div>
  )
}

function OrganizationSettings() {
  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">Organization Settings</h2>
      <div className="space-y-4 max-w-md">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Organization Name
          </label>
          <input type="text" className="input" placeholder="Your Organization" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Default Clustering Threshold
          </label>
          <input
            type="number"
            className="input"
            placeholder="0.7"
            min="0"
            max="1"
            step="0.1"
          />
        </div>
        <button className="btn-primary">Save Changes</button>
      </div>
    </div>
  )
}

function ApiSettings() {
  const [showKey, setShowKey] = useState(false)
  const apiKey = 'sk-xxxx-xxxx-xxxx-xxxx'

  const handleCopy = () => {
    navigator.clipboard.writeText(apiKey)
    toast.success('API key copied')
  }

  const handleRegenerate = () => {
    toast.success('API key regenerated')
  }

  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">API Keys</h2>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">API Key</label>
          <div className="flex gap-2">
            <input
              type={showKey ? 'text' : 'password'}
              value={apiKey}
              readOnly
              className="input flex-1"
            />
            <button onClick={() => setShowKey(!showKey)} className="btn-secondary">
              {showKey ? 'Hide' : 'Show'}
            </button>
            <button onClick={handleCopy} className="btn-secondary">
              Copy
            </button>
          </div>
        </div>
        <button onClick={handleRegenerate} className="btn-danger">
          Regenerate Key
        </button>
      </div>
    </div>
  )
}

function NotificationSettings() {
  const [emailNotifs, setEmailNotifs] = useState(true)
  const [clusterNotifs, setClusterNotifs] = useState(true)
  const [approvalNotifs, setApprovalNotifs] = useState(true)

  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">Notification Preferences</h2>
      <div className="space-y-4">
        <label className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={emailNotifs}
            onChange={(e) => setEmailNotifs(e.target.checked)}
            className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span>Email notifications</span>
        </label>
        <label className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={clusterNotifs}
            onChange={(e) => setClusterNotifs(e.target.checked)}
            className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span>New cluster alerts</span>
        </label>
        <label className="flex items-center gap-3">
          <input
            type="checkbox"
            checked={approvalNotifs}
            onChange={(e) => setApprovalNotifs(e.target.checked)}
            className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span>Approval requests</span>
        </label>
        <button className="btn-primary">Save Preferences</button>
      </div>
    </div>
  )
}
