// Mock user data for Admin UI demonstration
// This data simulates users with overlapping IP addresses to demonstrate the connection feature

// IP addresses that will be shared across users
const SHARED_IPS = {
  cluster1: ["192.168.1.100", "10.0.0.50", "203.45.67.89"],      // USR-001's main IPs
  cluster2: ["172.16.0.25", "192.168.3.50"],
  cluster3: ["85.120.45.67", "192.168.4.100"],
  cluster4: ["110.55.32.18", "45.67.89.123"],
  cluster5: ["200.45.78.90", "192.168.2.200"],
  cluster6: ["156.78.90.12", "10.10.10.50"],
  cluster7: ["89.123.45.67", "172.20.0.100"],
  cluster8: ["203.100.50.25", "192.168.10.10"]
};

// Cities for random assignment
const CITIES = [
  "New York, USA", "Los Angeles, USA", "Chicago, USA", "Houston, USA", "Miami, USA",
  "San Francisco, USA", "Seattle, USA", "Boston, USA", "Denver, USA", "Austin, USA",
  "London, UK", "Manchester, UK", "Birmingham, UK", "Edinburgh, UK",
  "Toronto, Canada", "Vancouver, Canada", "Montreal, Canada",
  "Sydney, Australia", "Melbourne, Australia", "Brisbane, Australia",
  "Berlin, Germany", "Munich, Germany", "Frankfurt, Germany",
  "Paris, France", "Lyon, France", "Marseille, France",
  "Tokyo, Japan", "Osaka, Japan", "Seoul, South Korea",
  "Singapore", "Hong Kong", "Dubai, UAE",
  "São Paulo, Brazil", "Mexico City, Mexico", "Buenos Aires, Argentina"
];

// First names and last names for generating users
const FIRST_NAMES = [
  "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
  "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen",
  "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth",
  "Nancy", "Betty", "Margaret", "Sandra", "Ashley", "Dorothy", "Kimberly", "Emily", "Donna", "Michelle",
  "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie", "Quinn", "Avery", "Cameron"
];

const LAST_NAMES = [
  "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
  "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
  "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
  "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"
];

// Generate a random date within a range
function randomDate(start, end) {
  return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime())).toISOString();
}

// Generate a unique IP address
function generateIP() {
  return `${Math.floor(Math.random() * 223) + 1}.${Math.floor(Math.random() * 256)}.${Math.floor(Math.random() * 256)}.${Math.floor(Math.random() * 256)}`;
}

// Build the mock users array
const MOCK_USERS = [];

// USR-001: The main user with connections to at least 8 others
MOCK_USERS.push({
  user_id: "USR-001",
  name: "John Doe",
  email: "john.doe@email.com",
  profile_pic: "https://api.dicebear.com/7.x/avataaars/svg?seed=John",
  signup_location: "New York, USA",
  signup_date: "2024-01-15T10:30:00Z",
  last_activity: "2026-01-29T09:15:00Z",
  status: "active",
  plan: "paid",
  ip_addresses: [...SHARED_IPS.cluster1, SHARED_IPS.cluster6[0], SHARED_IPS.cluster7[0]]
});

// Users 2-12: Original users with various connections
const originalUsers = [
  { id: "USR-002", name: "Jane Smith", email: "jane.smith@email.com", city: "Los Angeles, USA", status: "active", plan: "free", ips: [SHARED_IPS.cluster1[0], SHARED_IPS.cluster2[0]] },
  { id: "USR-003", name: "Michael Chen", email: "m.chen@email.com", city: "San Francisco, USA", status: "active", plan: "paid", ips: [SHARED_IPS.cluster1[1], SHARED_IPS.cluster5[1]] },
  { id: "USR-004", name: "Sarah Johnson", email: "sarah.j@email.com", city: "Chicago, USA", status: "active", plan: "paid", ips: [SHARED_IPS.cluster1[2], SHARED_IPS.cluster1[1]] },
  { id: "USR-005", name: "David Wilson", email: "d.wilson@email.com", city: "Miami, USA", status: "inactive", plan: "free", ips: [SHARED_IPS.cluster2[0], SHARED_IPS.cluster2[1]] },
  { id: "USR-006", name: "Emily Brown", email: "emily.b@email.com", city: "London, UK", status: "active", plan: "paid", ips: [SHARED_IPS.cluster3[0], SHARED_IPS.cluster3[1]] },
  { id: "USR-007", name: "James Taylor", email: "j.taylor@email.com", city: "London, UK", status: "active", plan: "free", ips: [SHARED_IPS.cluster3[0], SHARED_IPS.cluster6[0]] },
  { id: "USR-008", name: "Lisa Anderson", email: "lisa.a@email.com", city: "Sydney, Australia", status: "active", plan: "paid", ips: [SHARED_IPS.cluster1[2], SHARED_IPS.cluster4[0]] },
  { id: "USR-009", name: "Robert Martinez", email: "r.martinez@email.com", city: "Toronto, Canada", status: "inactive", plan: "free", ips: [SHARED_IPS.cluster4[1], SHARED_IPS.cluster7[0]] },
  { id: "USR-010", name: "Amanda White", email: "a.white@email.com", city: "Berlin, Germany", status: "active", plan: "paid", ips: [SHARED_IPS.cluster4[1], SHARED_IPS.cluster6[1]] },
  { id: "USR-011", name: "Chris Lee", email: "c.lee@email.com", city: "Seoul, South Korea", status: "active", plan: "paid", ips: [SHARED_IPS.cluster4[0], SHARED_IPS.cluster8[0]] },
  { id: "USR-012", name: "Nicole Garcia", email: "n.garcia@email.com", city: "Mexico City, Mexico", status: "active", plan: "free", ips: [SHARED_IPS.cluster5[1], SHARED_IPS.cluster5[0]] }
];

originalUsers.forEach((u, idx) => {
  MOCK_USERS.push({
    user_id: u.id,
    name: u.name,
    email: u.email,
    profile_pic: `https://api.dicebear.com/7.x/avataaars/svg?seed=${u.name.split(' ')[0]}`,
    signup_location: u.city,
    signup_date: randomDate(new Date('2024-01-01'), new Date('2024-12-31')),
    last_activity: randomDate(new Date('2026-01-01'), new Date('2026-01-29')),
    status: u.status,
    plan: u.plan,
    ip_addresses: [...u.ips, generateIP()]
  });
});

// Generate additional users (USR-013 to USR-112) - 100 more users
for (let i = 13; i <= 112; i++) {
  const firstName = FIRST_NAMES[Math.floor(Math.random() * FIRST_NAMES.length)];
  const lastName = LAST_NAMES[Math.floor(Math.random() * LAST_NAMES.length)];
  const name = `${firstName} ${lastName}`;
  const userId = `USR-${String(i).padStart(3, '0')}`;
  const city = CITIES[Math.floor(Math.random() * CITIES.length)];
  const status = Math.random() > 0.2 ? "active" : "inactive";
  const plan = Math.random() > 0.6 ? "paid" : "free";
  
  // Assign IPs - some will share with USR-001's cluster, others with random clusters
  const userIPs = [generateIP()];
  
  // 20% chance to share an IP with USR-001's cluster1
  if (Math.random() < 0.2) {
    userIPs.push(SHARED_IPS.cluster1[Math.floor(Math.random() * SHARED_IPS.cluster1.length)]);
  }
  
  // 15% chance to share with cluster6 (also connected to USR-001)
  if (Math.random() < 0.15) {
    userIPs.push(SHARED_IPS.cluster6[Math.floor(Math.random() * SHARED_IPS.cluster6.length)]);
  }
  
  // 15% chance to share with cluster7 (also connected to USR-001)
  if (Math.random() < 0.15) {
    userIPs.push(SHARED_IPS.cluster7[Math.floor(Math.random() * SHARED_IPS.cluster7.length)]);
  }
  
  // Random chance to be in other clusters
  const clusterKeys = Object.keys(SHARED_IPS);
  if (Math.random() < 0.3) {
    const randomCluster = SHARED_IPS[clusterKeys[Math.floor(Math.random() * clusterKeys.length)]];
    userIPs.push(randomCluster[Math.floor(Math.random() * randomCluster.length)]);
  }
  
  // Add another unique IP
  userIPs.push(generateIP());
  
  MOCK_USERS.push({
    user_id: userId,
    name: name,
    email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@email.com`,
    profile_pic: `https://api.dicebear.com/7.x/avataaars/svg?seed=${firstName}${i}`,
    signup_location: city,
    signup_date: randomDate(new Date('2024-01-01'), new Date('2025-12-31')),
    last_activity: randomDate(new Date('2026-01-01'), new Date('2026-01-29')),
    status: status,
    plan: plan,
    ip_addresses: [...new Set(userIPs)] // Remove duplicates
  });
}

// Helper function to find users connected by IP
function findConnectedUsers(userId) {
  const user = MOCK_USERS.find(u => u.user_id === userId);
  if (!user) return [];

  const userIPs = new Set(user.ip_addresses);
  const connections = [];

  MOCK_USERS.forEach(otherUser => {
    if (otherUser.user_id === userId) return;
    
    const sharedIPs = otherUser.ip_addresses.filter(ip => userIPs.has(ip));
    if (sharedIPs.length > 0) {
      connections.push({
        ...otherUser,
        shared_ips: sharedIPs,
        shared_ip_count: sharedIPs.length
      });
    }
  });

  return connections.sort((a, b) => b.shared_ip_count - a.shared_ip_count);
}

// Helper function to search users
function searchUsers(query) {
  if (!query || query.trim() === '') return MOCK_USERS;
  
  const lowerQuery = query.toLowerCase().trim();
  return MOCK_USERS.filter(user => 
    user.user_id.toLowerCase().includes(lowerQuery) ||
    user.name.toLowerCase().includes(lowerQuery) ||
    user.email.toLowerCase().includes(lowerQuery)
  );
}

// Helper function to format relative time
function formatRelativeTime(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
  if (diffDays < 7) return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
  return date.toLocaleDateString();
}

// Make available globally
window.MOCK_USERS = MOCK_USERS;
window.findConnectedUsers = findConnectedUsers;
window.searchUsers = searchUsers;
window.formatRelativeTime = formatRelativeTime;

// Log for debugging
console.log(`Loaded ${MOCK_USERS.length} mock users`);
console.log(`USR-001 connections:`, findConnectedUsers('USR-001').length);
