import {VividKeyframe} from "./VividKeyframe";

export class KeyframeUtils {
    public static getUrl(kf: VividKeyframe): string {
        return "http://localhost:9080/" + kf.video + "/shot" + kf.video + "_" + kf.idx + ".png";
    }

    public static getTimelineUrls(kf: VividKeyframe): string[] {
        const numToDisplay = 10;
        const beginIndex = Math.max(Math.abs(kf.idx - numToDisplay / 2), 1);
        const endIndex = Math.min(Math.abs(kf.idx + numToDisplay / 2), kf.totalKfsVid);
        const resultArr = [];
        for (let i = beginIndex; i <= endIndex; i++) {
            resultArr.push("http://localhost:9080/" + kf.video + "/shot" + kf.video + "_" + i + ".png");
        }
        return resultArr;
    }
}
