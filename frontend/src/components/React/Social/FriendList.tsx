import React from 'react';

interface Friend {
  id: string;
  name: string;
  level: number;
  status: 'online' | 'offline';
  avatar: string;
}

const mockFriends: Friend[] = [
  { id: '1', name: 'Alex Rivers', level: 12, status: 'online', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alex' },
  { id: '2', name: 'Sam Chen', level: 8, status: 'online', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sam' },
  { id: '3', name: 'Jordan Smith', level: 15, status: 'offline', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Jordan' },
  { id: '4', name: 'Taylor Reed', level: 5, status: 'online', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Taylor' },
];

export default function FriendList() {
  return (
    <div className="space-y-4">
      {mockFriends.map((friend) => (
        <div 
          key={friend.id} 
          className="flex items-center justify-between p-4 bg-surface-container-lowest rounded-xl border border-outline-variant/30 hover:border-secondary/50 transition-colors group"
        >
          <div className="flex items-center gap-4">
            <div className="relative">
              <img 
                src={friend.avatar} 
                alt={friend.name} 
                className="w-12 h-12 rounded-full bg-surface-container-high" 
              />
              <div className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-surface-container-lowest ${friend.status === 'online' ? 'bg-secondary' : 'bg-outline-variant'}`}></div>
            </div>
            <div>
              <h4 className="font-display font-bold text-on-surface">{friend.name}</h4>
              <div className="flex items-center gap-2">
                <span className="text-xs text-on-surface/50 font-medium tracking-wide uppercase">Nivel</span>
                <span className="ai-chip !py-0 !px-2 !text-[10px]">{friend.level}</span>
              </div>
            </div>
          </div>
          
          <button className="opacity-0 group-hover:opacity-100 p-2 text-on-surface/40 hover:text-secondary transition-all">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
          </button>
        </div>
      ))}
      {mockFriends.length === 0 && (
        <p className="text-center py-10 text-on-surface/40 font-medium">Aún no tienes amigos. ¡Agrega uno!</p>
      )}
    </div>
  );
}