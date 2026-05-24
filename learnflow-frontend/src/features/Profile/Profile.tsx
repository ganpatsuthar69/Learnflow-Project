import { useState } from "react";
import ProfileView from "../../components/Profile/ProfileView";
import EditProfile from "../../components/Profile/EditProfile";
import AppLayout from "../../components/AppLayout";

export default function Profile() {
  const [isEditing, setIsEditing] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleSave = () => {
    setIsEditing(false);
    setRefreshKey(prev => prev + 1);
  };

  return (
    <AppLayout>
      <div className="py-8 max-w-5xl mx-auto">
        {isEditing ? (
          <EditProfile
            onCancel={() => setIsEditing(false)}
            onSaveComplete={handleSave}
          />
        ) : (
          <ProfileView
            key={refreshKey}
            onEdit={() => setIsEditing(true)}
          />
        )}
      </div>
    </AppLayout>
  );
}