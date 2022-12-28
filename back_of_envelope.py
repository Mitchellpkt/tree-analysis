num_rings: int = 5_573_404
pairwise_rate_Hz: float = 4_525_604_048 / 53
num_checks: int = int((num_rings**2) / 2)
estimated_time_sec: float = num_checks / pairwise_rate_Hz
print(f"Check rate (Hz): {pairwise_rate_Hz:.2f}")
print(f"Number of ring pair checks: {num_checks}")
print(f"Estimated time: {estimated_time_sec:.2f} seconds")
print(f"Estimated time: {estimated_time_sec / (24 * 60 * 60):.2f} days")
