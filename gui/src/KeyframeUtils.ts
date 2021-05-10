import {VividKeyframe} from "./VividKeyframe";

export class KeyframeUtils {
    public static getUrl(kf: VividKeyframe): string {
        if (kf.title === "n/A") {
            return "https://i.stack.imgur.com/6M513.png";
        }
        return "https://iten.engineering/files/keyframes/" + kf.video + "/shot" + kf.video + "_" + kf.idx + "_RKF.png";
    }

    public static getTimelineUrls(kf: VividKeyframe): string[] {
        const numToDisplay = 10;
        const beginIndex = Math.max(Math.abs(kf.idx - numToDisplay / 2), 1);
        const endIndex = Math.min(Math.abs(kf.idx + numToDisplay / 2), kf.totalKfsVid);
        const resultArr = [];
        for (let i = beginIndex; i <= endIndex; i++) {
            resultArr.push("http://localhost:9080/" + kf.video + "/shot" + kf.video + "_" + i + "_RKF.png");
        }
        return resultArr;
    }
}
