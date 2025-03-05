import json
import pandas as pd

from datetime import datetime

def extrct_ftrs(d_json, app_date):
    ret_dict = {
            "tot_claim_cnt_l180d": -3,
            "disb_bank_loan_wo_tbc": -3,
            "day_sinlastloan": -3,
        }
    try:
        if pd.isna(d_json) or d_json.strip() == "":
            return ret_dict

        conts = json.loads(d_json)

        if isinstance(conts, dict):
            conts = [conts]

        if not isinstance(conts, list) or not all(isinstance(cont, dict) for cont in conts):
            print('--not correct json--',conts)
            return ret_dict

        #######################################
        exc_banks = {'LIZ', 'LOM', 'MKO', 'SUG', None}

        claim_dates = []
        sum_2f = 0
        for cont in conts:
            # print('--cont--', cont)
            claim_date_str = cont.get("claim_date").strip()
            cont_date_str = cont.get("contract_date", "").strip()
            bank = cont.get("bank")

            if claim_date_str:
                try:
                    claim_date = datetime.strptime(claim_date_str, "%d.%m.%Y")
                    claim_dates.append(claim_date)
                except ValueError:
                    print('--error in claim_date')
                    continue  # Skip invalid date

            if cont_date_str and bank not in exc_banks:
                loan_summa = cont.get("loan_summa", 0)
                if str(loan_summa).isdigit():
                    sum_2f += int(loan_summa)

        if claim_dates:
            last_loan_date = max(claim_dates)
            days_3f = (app_date - last_loan_date).days
        else:
            days_3f = -3

        f1_recent_claims = [date for date in claim_dates if (app_date - date).days <= 180]
        rc_claims = len(f1_recent_claims)
        tot_claim_cnt_l180d = -3 if rc_claims == 0 else rc_claims
        disb_bank_loan_wo_tbc = -1 if sum_2f == 0 else sum_2f
        day_sinlastloan = -1 if days_3f == 0 else days_3f

        return {
            "tot_claim_cnt_l180d": tot_claim_cnt_l180d,
            "disb_bank_loan_wo_tbc": disb_bank_loan_wo_tbc,
            "day_sinlastloan": day_sinlastloan,
        }

    except Exception as e:
        print(f"Error in JSON: {d_json} -> {e}")
        return ret_dict


def main():
    f_path = 'data.csv'
    df = pd.read_csv(f_path)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.expand_frame_repr", False)

    df["application_date"] = pd.to_datetime(df["application_date"]).dt.tz_localize(None)

    features_df = df.apply(lambda row: extrct_ftrs(row["contracts"], row["application_date"]), axis=1).apply(pd.Series)
    final_result_df = df[["id", "application_date"]].join(features_df)

    # Save to CSV
    output_file = "contract_features.csv"
    final_result_df.to_csv(output_file, index=False)

    print(f"Completed! File -> {output_file}")


if __name__ == '__main__':
    main()
