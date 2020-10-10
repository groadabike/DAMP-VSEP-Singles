import numpy as np
import librosa
# Ignore librosa warnings
import warnings

warnings.filterwarnings('ignore')


def load_data(audio_path, sample_rate):
    x, _ = librosa.load(str(audio_path),
                        sr=sample_rate,
                        mono=True,
                        res_type='kaiser_best'
                        )
    return x


def get_amplitude_scaling_factor(v, b, snr=0):
    """Given v and b, return the scaler s according to the snr.
    Args:
      v: ndarray, vocal.
      b: ndarray, backgroun.
      snr: float, SNR. Default=0
    Outputs:
      float, scaler.
    """

    def _rms(y):
        return np.sqrt(np.mean(np.abs(y) ** 2, axis=0, keepdims=False))

    v[v == 0.] = 1e-8  # Replace zero values by a small value
    b[b == 0.] = 1e-8  # Replace zero values by a small value
    original_sn_rms_ratio = _rms(v) / _rms(b)
    target_sn_rms_ratio = 10. ** (float(snr) / 20.)
    signal_scaling_factor = target_sn_rms_ratio / original_sn_rms_ratio
    return signal_scaling_factor


def xcorr(x, y, normed=True):
    """
    Cross correlation of two signals of equal length
    Based on https://github.com/colizoli/xcorr_python

    Args:
        x (np.array): Singal 1
        y (np.array): Signal 2
        normed (boolean): Default ``'True'``
            * Function return correlation coefficients if normed=``'True'``
            * Function return inner products if normed=``'False'``
    Returns:
    c = correlation
    """
    Nx = len(x)
    if Nx != len(y):
        if Nx > len(y):
            result = np.zeros(x.shape)
            result[:y.shape[0]] = y
            y = result
        else:
            result = np.zeros(y.shape)
            result[:x.shape[0]] = x
            x = result

    c = np.correlate(x, y, mode='full')
    if normed:
        n = np.sqrt(np.dot(x, x) * np.dot(y, y))  # this is the transformation function
        c = np.true_divide(c, n)
    return c


def xcorr_searcher(x, y):
    max_corr = 0
    max_lag = 0

    # progresively, make cuts of mix and
    # calculate cross correlation with the
    # target segment
    for i in range(x.shape[0] - y.shape[0]):
        x1 = x[i:i + y.shape[0]]
        c = xcorr(x1, y)

        if max(c) > max_corr:
            max_corr = max(c)
            max_lag = i

    return max_lag, max_corr


def xcorr_searcher_max(x, y, sr, frame_length, hop_length, search_length=1):
    rms_mix = librosa.feature.rms(x, frame_length=frame_length, hop_length=hop_length)[0]
    lags = {}
    for i in range(30):
        search_segment = y[int(i * sr):int((i + search_length) * sr)]
        if len(search_segment) < int(search_length * sr):
            break
        else:
            rms_vocal_segment = librosa.feature.rms(search_segment, frame_length=frame_length,
                                                    hop_length=hop_length)[0]
            lag, corr = xcorr_searcher(rms_mix, rms_vocal_segment)
            time = librosa.frames_to_time(abs(lag), hop_length=hop_length, n_fft=frame_length, sr=sr)
            time = round(time - i, 4)
            if time in lags:
                lags[time] += 1
            else:
                lags[time] = 1
    l_values = list(lags.values())
    l_keys = list(lags.keys())
    if l_values[np.argmax(l_values)] < 3:
        idx_min = np.where(np.abs(l_keys) == np.min(np.abs(l_keys)))[0][0]
        return l_keys[idx_min]
    else:
        return l_keys[np.argmax(l_values)]
