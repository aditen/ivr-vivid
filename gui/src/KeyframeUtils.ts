import {VividKeyframe} from "./VividKeyframe";

export class KeyframeUtils {
    public static getUrl(kf: VividKeyframe): string {
        if (kf.title === "n/A") {
            return "https://i.stack.imgur.com/6M513.png";
        }
        return "https://iten.engineering/files/keyframes/" + kf.video + "/shot" + kf.video + "_" + kf.idx + "_RKF.png";
    }
}
