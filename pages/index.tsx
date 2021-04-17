import {NextPage} from "next";
import {AppBar, Icon, IconButton, Toolbar, Typography} from "@material-ui/core";
import * as React from "react";
import {useState} from "react";
import Head from "next/dist/next-server/lib/head";
import {Rnd} from "react-rnd";

const MainPage: NextPage = () => {

    const [figures, setFigures] = useState(["test"]);

    return (<>
        <Head>
            <title>IVR</title>
            <link rel="icon" href="/favicon.ico"/>
            <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons"/>
        </Head>
        <AppBar position={"static"}>
            <Toolbar style={{padding: 20}}>
                <Typography variant={"h3"} align={"center"}>
                    Interactive Video Retrieval</Typography>
            </Toolbar>
        </AppBar>
        <div>
            <IconButton onClick={() => {
                setFigures([...figures, "second"])
            }}><Icon>add</Icon></IconButton>
            <IconButton onClick={() => {
                setFigures([])
            }}><Icon>delete</Icon></IconButton>
        </div>
        <div style={{
            width: '500px',
            height: '500px',
            borderColor: "black",
            borderWidth: "medium",
            borderStyle: "solid"
        }}>
            {figures.map(fig => <Rnd bounds={"parent"} default={{x: 0, y: 0, width: 100, height: 100}} style={{
                borderColor: "black",
                borderWidth: "medium",
                borderStyle: "dotted"
            }}>
                <img draggable={false} style={{width: "100%", height: "100%"}}
                     src={"https://image.spreadshirtmedia.net/image-server/v1/mp/products/T1302A1MPA3321PT24X0Y0D170309227FS1911/views/1,width=378,height=378,appearanceId=1,backgroundColor=F2F2F2/strichmaennchen-design-stickman-trend-geschenkidee-poster.jpg"}/>
            </Rnd>)}

        </div>
    </>)
};

export default MainPage;
