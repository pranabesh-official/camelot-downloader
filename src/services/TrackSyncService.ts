// Firebase removed - TrackSyncService now uses local storage only

export interface TrackMetadataPayload {
    id: string;
    filename: string;
    file_path?: string;
    key?: string;
    scale?: string;
    key_name?: string;
    camelot_key?: string;
    bpm?: number;
    energy_level?: number;
    duration?: number;
    file_size?: number;
    bitrate?: number;
    analysis_date?: string;
    cue_points?: number[];
    track_id?: string;
    id3?: any;
}

export async function upsertUserTrack(userId: string, track: TrackMetadataPayload): Promise<void> {
    // Firebase removed - this function now does nothing
    console.log('[Local] Track sync disabled (Firebase removed):', track.filename);
}

export async function upsertManyUserTracks(userId: string, tracks: TrackMetadataPayload[]): Promise<void> {
    // Firebase removed - this function now does nothing
    console.log('[Local] Batch track sync disabled (Firebase removed):', tracks.length, 'tracks');
}

export async function writeAuthHealth(userId: string): Promise<void> {
    // Firebase removed - this function now does nothing
    console.log('[Local] Auth health check disabled (Firebase removed)');
}

/**
 * Save song analysis data - Firebase removed, now uses local storage only
 */
export async function saveToAnalysisSongs(userId: string, track: TrackMetadataPayload): Promise<void> {
    // Firebase removed - this function now does nothing
    console.log('[Local] Analysis songs sync disabled (Firebase removed):', track.filename);
}


