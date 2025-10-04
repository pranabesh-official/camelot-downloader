import './App.css';
import YouTubeMusic from './components/YouTubeMusic';
import DownloadManager from './components/DownloadManager';
import React, { useState, useEffect, useRef } from 'react';

// Simplified interface for downloaded tracks
export interface DownloadedTrack {
    id: string;
    filename: string;
    file_path?: string;
    title?: string;
    artist?: string;
    duration?: number;
    file_size?: number;
    download_date?: string;
}

// Legacy Song interface for backward compatibility with unused components
export interface Song {
    id: string;
    filename: string;
    file_path?: string;
    title?: string;
    artist?: string;
    key?: string;
    scale?: string;
    key_name?: string;
    camelot_key?: string;
    bpm?: number;
    energy_level?: number;
    duration?: number;
    file_size?: number;
    bitrate?: number;
    status?: string;
    analysis_date?: string;
    cue_points?: number[];
    track_id?: string;
    id3?: any;
    cover_art?: string;
    cover_art_extracted?: boolean;
    analysis_status?: 'pending' | 'analyzing' | 'completed' | 'failed';
    id3_tags_written?: boolean;
    last_analysis_attempt?: string;
    analysis_attempts?: number;
    file_hash?: string;
    prevent_reanalysis?: boolean;
}

// Legacy Playlist interface for backward compatibility
export interface Playlist {
    id: string;
    name: string;
    songs: Song[];
    created_at: string;
    updated_at: string;
}

// Simple text title component
const TitleComponent = () => {
    return <div className="app-title">Camelot Downloader</div>;
};

// Simplified Settings component
const SettingsComponent: React.FC<{
    downloadPath: string;
    setDownloadPath: (path: string) => void;
    isDownloadPathSet: boolean;
    setIsDownloadPathSet: (set: boolean) => void;
    isLoadingSettings: boolean;
    setIsLoadingSettings: (loading: boolean) => void;
    showSaveSuccess: boolean;
    setShowSaveSuccess: (show: boolean) => void;
}> = ({
    downloadPath,
    setDownloadPath,
    isDownloadPathSet,
    setIsDownloadPathSet,
    isLoadingSettings,
    setIsLoadingSettings,
    showSaveSuccess,
    setShowSaveSuccess
}) => {
    const handleBrowseFolder = async () => {
        setIsLoadingSettings(true);
        try {
            if (typeof window !== 'undefined' && (window as any).require) {
                const { ipcRenderer } = (window as any).require('electron');
                const result = await ipcRenderer.invoke('select-download-folder');
                
                if (result && !result.canceled && result.filePaths.length > 0) {
                    const selectedPath = result.filePaths[0];
                    setDownloadPath(selectedPath);
                    setIsDownloadPathSet(true);
                    
                    localStorage.setItem('downloadPath', selectedPath);
                    localStorage.setItem('isDownloadPathSet', 'true');
                    
                    setShowSaveSuccess(true);
                    setTimeout(() => setShowSaveSuccess(false), 3000);
                }
            } else {
                const path = prompt('Enter download path:');
                if (path) {
                    setDownloadPath(path);
                    setIsDownloadPathSet(true);
                    localStorage.setItem('downloadPath', path);
                    localStorage.setItem('isDownloadPathSet', 'true');
                    setShowSaveSuccess(true);
                    setTimeout(() => setShowSaveSuccess(false), 3000);
                }
            }
        } catch (error) {
            console.error('Error selecting folder:', error);
        } finally {
            setIsLoadingSettings(false);
        }
    };

    return (
        <div className="settings-page">
            {showSaveSuccess && (
                <div className="success-notification">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M9 12l2 2 4-4"/>
                        <circle cx="12" cy="12" r="10"/>
                    </svg>
                    Settings saved successfully!
                </div>
            )}

            <div className="settings-content">
                <div className="settings-header">
                    <h1>Settings</h1>
                </div>

                <div className="settings-section">
                    <h2>Download Location</h2>
                    
                    <div className="setting-group">
                        <label>Download Folder</label>
                        <div className="folder-selector">
                            <input 
                                type="text" 
                                value={downloadPath || 'No folder selected'} 
                                readOnly 
                                className="folder-input"
                                placeholder="Select a download folder..."
                            />
                            <button 
                                onClick={handleBrowseFolder}
                                className="browse-button"
                                disabled={isLoadingSettings}
                            >
                                {isLoadingSettings ? (
                                    <div className="spinner"></div>
                                ) : (
                                    <>
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                                        </svg>
                                        Browse
                                    </>
                                )}
                            </button>
                        </div>
                        
                        {isDownloadPathSet ? (
                            <div className="status-message success">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M9 12l2 2 4-4"/>
                                    <circle cx="12" cy="12" r="10"/>
                                </svg>
                                Download path configured
                            </div>
                        ) : (
                            <div className="status-message warning">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                                    <line x1="12" y1="9" x2="12" y2="13"/>
                                    <line x1="12" y1="17" x2="12.01" y2="17"/>
                                </svg>
                                Please select a download folder
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

const App: React.FC = () => {
    // State for YouTube downloading and settings
    const [downloadPath, setDownloadPath] = useState<string>('');
    const [isDownloadPathSet, setIsDownloadPathSet] = useState(false);
    const [apiPort, setApiPort] = useState(5002);
    const [apiSigningKey, setApiSigningKey] = useState("devkey");
    const [currentView, setCurrentView] = useState<'youtube' | 'settings'>('youtube');
    const [isLoadingSettings, setIsLoadingSettings] = useState(false);
    const [showSaveSuccess, setShowSaveSuccess] = useState(false);
    
    // Ref for DownloadManager
    const downloadManagerRef = useRef<any>(null);

    // Load settings from localStorage
    useEffect(() => {
        const savedPath = localStorage.getItem('downloadPath');
        const savedPathSet = localStorage.getItem('isDownloadPathSet') === 'true';
        
        if (savedPath) {
            setDownloadPath(savedPath);
            setIsDownloadPathSet(savedPathSet);
        }
    }, []);

    // Check if running in Electron and get API details
    useEffect(() => {
        const isElectron = !!(window as any).require;
        
        if (isElectron) {
            try {
                const { ipcRenderer } = (window as any).require('electron');
                
                // Request API details from Electron main process
                ipcRenderer.send('getApiDetails');
                
                // Listen for API details response
                ipcRenderer.on('apiDetails', (event: any, details: string) => {
                    try {
                        const apiInfo = JSON.parse(details);
                        console.log('Received API details from Electron:', apiInfo);
                        setApiPort(apiInfo.port);
                        setApiSigningKey(apiInfo.signingKey);
                    } catch (error) {
                        console.error('Error parsing API details:', error);
                    }
                });
                
                // Listen for API details error
                ipcRenderer.on('apiDetailsError', (event: any, error: string) => {
                    console.error('Error getting API details:', error);
                });
                
                // Cleanup listeners
                return () => {
                    ipcRenderer.removeAllListeners('apiDetails');
                    ipcRenderer.removeAllListeners('apiDetailsError');
                };
            } catch (error) {
                console.error('Error setting up Electron IPC:', error);
            }
        }
    }, []);

    return (
        <div className="App">
            <header className="App-header">
                <div className="header-content">
                    <div className="brand">
                        <TitleComponent />
                    </div>
                    <nav className="nav-tabs">
                        <button 
                            className={`nav-tab ${currentView === 'youtube' ? 'active' : ''}`}
                            onClick={() => setCurrentView('youtube')}
                        >
                            Downloader
                        </button>
                        <button 
                            className={`nav-tab ${currentView === 'settings' ? 'active' : ''}`}
                            onClick={() => setCurrentView('settings')}
                        >
                            Settings
                        </button>
                    </nav>
                </div>
            </header>

            <main className="App-main">
                {currentView === 'youtube' && (
                    <>
                        <YouTubeMusic 
                            downloadPath={downloadPath}
                            isDownloadPathSet={isDownloadPathSet}
                            apiPort={apiPort}
                            apiSigningKey={apiSigningKey}
                            downloadManagerRef={downloadManagerRef}
                            onDownloadComplete={(song) => {
                                console.log('Download completed:', song);
                            }}
                        />
                        <DownloadManager
                            ref={downloadManagerRef}
                            apiPort={apiPort}
                            apiSigningKey={apiSigningKey}
                            downloadPath={downloadPath}
                            isDownloadPathSet={isDownloadPathSet}
                            onDownloadComplete={(song) => {
                                console.log('Download completed:', song);
                            }}
                        />
                    </>
                )}
                
                {currentView === 'settings' && (
                    <SettingsComponent
                        downloadPath={downloadPath}
                        setDownloadPath={setDownloadPath}
                        isDownloadPathSet={isDownloadPathSet}
                        setIsDownloadPathSet={setIsDownloadPathSet}
                        isLoadingSettings={isLoadingSettings}
                        setIsLoadingSettings={setIsLoadingSettings}
                        showSaveSuccess={showSaveSuccess}
                        setShowSaveSuccess={setShowSaveSuccess}
                    />
                )}
            </main>
        </div>
    );
};

export default App;