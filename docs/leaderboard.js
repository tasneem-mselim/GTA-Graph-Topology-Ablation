const LEADERBOARD_CONFIG = {
    csvPath: './leaderboard.csv',
    sortBy: 'validation_f1_perturbed',
    primaryScoreField: 'validation_f1_perturbed', // fix overwrite
    fieldNames: {
        team_name: 'Team',
        validation_f1_ideal: 'F1 Ideal',
        validation_f1_perturbed: 'F1 Perturbed',
        robustness_gap: 'Robustness Gap',
    },
    fieldFormatters: {
        validation_f1_ideal: (v) => Number.isFinite(v) ? v.toFixed(6) : v,
        validation_f1_perturbed: (v) => Number.isFinite(v) ? v.toFixed(6) : v,
        robustness_gap: (v) => Number.isFinite(v) ? v.toFixed(6) : v,
    }
};
