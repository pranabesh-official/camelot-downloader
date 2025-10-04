// Firebase removed - UserProfileService now uses local storage only

interface User {
  uid: string;
  email?: string | null;
  displayName?: string | null;
}

export interface UserProfile {
  stageName: string;
  realName?: string;
  email: string;
  experienceLevel: 'beginner' | 'intermediate' | 'advanced' | 'professional';
  musicGenres: string[];
  preferredBPM: { min: number; max: number };
  setupComplete: boolean;
  createdAt: any;
  updatedAt: any;
  // Additional profile fields
  bio?: string;
  location?: string;
  socialLinks?: {
    instagram?: string;
    twitter?: string;
    soundcloud?: string;
    spotify?: string;
  };
  preferences?: {
    theme: 'dark' | 'light' | 'auto';
    notifications: boolean;
    autoSync: boolean;
    defaultBPMRange: { min: number; max: number };
  };
  stats?: {
    totalTracksAnalyzed: number;
    totalPlaylistsCreated: number;
    totalMixTime: number; // in minutes
    favoriteGenres: string[];
  };
}

export class UserProfileService {
  private static instance: UserProfileService;
  
  public static getInstance(): UserProfileService {
    if (!UserProfileService.instance) {
      UserProfileService.instance = new UserProfileService();
    }
    return UserProfileService.instance;
  }

  /**
   * Get user profile from local storage
   */
  async getUserProfile(user: User): Promise<UserProfile | null> {
    try {
      const stored = localStorage.getItem(`userProfile_${user.uid}`);
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      console.error('Error getting user profile:', error);
      return null;
    }
  }

  /**
   * Create or update user profile in local storage
   */
  async saveUserProfile(user: User, profileData: Partial<UserProfile>): Promise<void> {
    try {
      const existingProfile = await this.getUserProfile(user);
      
      const profileToSave = {
        ...existingProfile,
        ...profileData,
        email: user.email || '',
        updatedAt: new Date().toISOString(),
        ...(existingProfile ? {} : { createdAt: new Date().toISOString() })
      };

      localStorage.setItem(`userProfile_${user.uid}`, JSON.stringify(profileToSave));
    } catch (error) {
      console.error('Error saving user profile:', error);
      throw new Error('Failed to save user profile');
    }
  }

  /**
   * Check if user has completed onboarding
   */
  async hasCompletedOnboarding(user: User): Promise<boolean> {
    try {
      const profile = await this.getUserProfile(user);
      return profile?.setupComplete || false;
    } catch (error) {
      console.error('Error checking onboarding status:', error);
      return false;
    }
  }

  /**
   * Update user stats (called after actions like analyzing tracks, creating playlists)
   */
  async updateUserStats(user: User, statsUpdate: Partial<UserProfile['stats']>): Promise<void> {
    try {
      const currentProfile = await this.getUserProfile(user);
      
      const updatedStats = {
        totalTracksAnalyzed: 0,
        totalPlaylistsCreated: 0,
        totalMixTime: 0,
        favoriteGenres: [],
        ...currentProfile?.stats,
        ...statsUpdate
      };

      await this.saveUserProfile(user, {
        stats: updatedStats,
        updatedAt: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error updating user stats:', error);
      // Don't throw error for stats updates as they're not critical
    }
  }

  /**
   * Update user preferences
   */
  async updateUserPreferences(user: User, preferences: Partial<UserProfile['preferences']>): Promise<void> {
    try {
      const currentProfile = await this.getUserProfile(user);
      
      const updatedPreferences = {
        theme: 'dark' as const,
        notifications: true,
        autoSync: true,
        defaultBPMRange: { min: 120, max: 140 },
        ...currentProfile?.preferences,
        ...preferences
      };

      await this.saveUserProfile(user, {
        preferences: updatedPreferences,
        updatedAt: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error updating user preferences:', error);
      throw new Error('Failed to update user preferences');
    }
  }

  /**
   * Get user's preferred BPM range for track suggestions
   */
  async getUserPreferredBPM(user: User): Promise<{ min: number; max: number }> {
    try {
      const profile = await this.getUserProfile(user);
      return profile?.preferredBPM || { min: 120, max: 140 };
    } catch (error) {
      console.error('Error getting user BPM preferences:', error);
      return { min: 120, max: 140 };
    }
  }

  /**
   * Get user's preferred music genres for filtering
   */
  async getUserPreferredGenres(user: User): Promise<string[]> {
    try {
      const profile = await this.getUserProfile(user);
      return profile?.musicGenres || [];
    } catch (error) {
      console.error('Error getting user genre preferences:', error);
      return [];
    }
  }

  /**
   * Initialize default profile for new user
   */
  async initializeDefaultProfile(user: User): Promise<void> {
    try {
      const defaultProfile: Partial<UserProfile> = {
        stageName: user.displayName || 'DJ',
        realName: user.displayName || '',
        email: user.email || '',
        experienceLevel: 'beginner',
        musicGenres: [],
        preferredBPM: { min: 120, max: 140 },
        setupComplete: false,
        preferences: {
          theme: 'dark',
          notifications: true,
          autoSync: true,
          defaultBPMRange: { min: 120, max: 140 }
        },
        stats: {
          totalTracksAnalyzed: 0,
          totalPlaylistsCreated: 0,
          totalMixTime: 0,
          favoriteGenres: []
        }
      };

      await this.saveUserProfile(user, defaultProfile);
    } catch (error) {
      console.error('Error initializing default profile:', error);
      throw new Error('Failed to initialize user profile');
    }
  }
}

export default UserProfileService;
