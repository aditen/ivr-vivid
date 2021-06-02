import {VividKeyframe} from "./VividKeyframe";

export class KeyframeUtils {
    public static getUrl(kf: VividKeyframe): string {
        return "http://localhost:9080/" + kf.video + "/shot" + kf.video + "_" + kf.idx + ".png";
    }

    public static getTimelineItems(kf: VividKeyframe): VividKeyframe[] {
        const numToDisplay = 10.;
        const beginIndex = Math.max(kf.idx - (numToDisplay / 2), 1);
        const endIndex = Math.min(kf.idx + (numToDisplay / 2), kf.totalKfsVid);
        const resultArr = [];
        for (let i = beginIndex; i <= endIndex; i++) {
            resultArr.push({...kf, idx: i});
        }
        return resultArr;
    }
}
