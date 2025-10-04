import React from 'react';
import { useState, useEffect } from 'react';
import OnboardingScreen from './OnboardingScreen';
import UserProfileService from '../services/UserProfileService';
import UserProfileDisplay from './UserProfileDisplay';

// Mock user for local storage
const mockUser = {
    uid: 'local-user',
    email: 'user@local.com',
    displayName: 'Local User'
};

const AuthGate: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const user = mockUser;
    const loading = false;
    const error = null;

    const [showOnboarding, setShowOnboarding] = useState(false);
    const [onboardingChecked, setOnboardingChecked] = useState(false);
    const [isCheckingOnboarding, setIsCheckingOnboarding] = useState(false);

    // Check if user needs onboarding when user changes
    useEffect(() => {
        const checkOnboardingStatus = async () => {
            if (user && !onboardingChecked && !isCheckingOnboarding) {
                // Immediately set checking state to prevent flash
                setIsCheckingOnboarding(true);
                
                try {
                    const userProfileService = UserProfileService.getInstance();
                    const hasCompletedOnboarding = await userProfileService.hasCompletedOnboarding(user);
                    
                    if (!hasCompletedOnboarding) {
                        // Set onboarding state immediately
                        setShowOnboarding(true);
                    }
                    setOnboardingChecked(true);
                } catch (error) {
                    console.error('Error checking onboarding status:', error);
                    // If there's an error, show onboarding to be safe
                    setShowOnboarding(true);
                    setOnboardingChecked(true);
                } finally {
                    setIsCheckingOnboarding(false);
                }
            } else if (!user) {
                setOnboardingChecked(false);
                setShowOnboarding(false);
                setIsCheckingOnboarding(false);
            }
        };

        checkOnboardingStatus();
    }, [user, onboardingChecked, isCheckingOnboarding]);

    const handleOnboardingComplete = async () => {
        console.log('🎉 Onboarding completed, triggering database cleanup...');
        
        // Trigger additional database cleanup after onboarding
        try {
            // Get API port and signing key (these should match the backend)
            const apiPort = 5002;
            const apiSigningKey = 'devkey';
            
            // Call database cleanup endpoint
            const response = await fetch(`http://127.0.0.1:${apiPort}/database/clear-all`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Signing-Key': apiSigningKey
                },
                body: JSON.stringify({})
            });

            if (response.ok) {
                console.log('✅ Database cleaned successfully after onboarding completion');
            } else {
                console.warn('⚠️ Database cleanup failed after onboarding, but continuing');
            }
        } catch (error) {
            console.warn('⚠️ Database cleanup error after onboarding (non-critical):', error);
        }
        
        setShowOnboarding(false);
    };

    const signOutUser = () => {
        // Firebase removed - sign out does nothing
        console.log('Sign out (Firebase removed)');
    };

    // Firebase removed - no loading or authentication screens needed

    // Show onboarding screen if user needs to complete setup
    if (showOnboarding && user) {
        return (
            <div style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                zIndex: 1000,
                animation: 'fadeIn 0.5s ease-out',
                background: 'var(--app-bg)'
            }}>
                <OnboardingScreen onComplete={handleOnboardingComplete} />
            </div>
        );
    }

    return (
        <div style={{ height: '100%' }}>
            {children}
        </div>
    );
};

export default AuthGate;


